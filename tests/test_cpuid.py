

import unittest
from cpuinfo import *
import helpers


class MockCPUID(CPUID):
	def __init__(self):
		super(MockCPUID, self).__init__()

	def _asm_func(self, restype=None, argtypes=(), byte_code=[]):
		raise Exception("FIXME: Add body of mock _asm_func")

	def _run_asm(self, *byte_code):
		expected = (b"\xB8\x02\x00\x00\x80",  # mov ax,0x8000000?
							b"\x0f\xa2"   # cpuid
							b"\x89\xC0"   # mov ax,ax
							b"\xC3"       # ret
					,)
		print('!!!!!! expected :', expected)
		print('!!!!!! byte_code:', byte_code)
		print('!!!!!! ==       :', expected == byte_code)

		# get_max_extension_support
		if byte_code == \
			(b"\xB8\x00\x00\x00\x80" # mov ax,0x80000000
			b"\x0f\xa2"               # cpuid
			b"\xC3",):               # ret
			return 0x8000001f

		# get_cache
		if byte_code == \
			(b"\xB8\x06\x00\x00\x80"  # mov ax,0x80000006
			b"\x0f\xa2"                # cpuid
			b"\x89\xC8"                # mov ax,cx
			b"\xC3",):                # ret))
			return 0x2006140

		# get_info
		if byte_code == \
			(self._one_eax(),  # mov eax,0x1"
			b"\x0f\xa2"                # cpuid
			b"\xC3",):                # ret
			return 0x800f82

		# get_processor_brand
		if byte_code == \
			(b"\xB8\x02\x00\x00\x80",  # mov ax,0x80000002
			b"\x0f\xa2"                # cpuid
			b"\x89\xC0"                # mov ax,ax
			b"\xC3",):                 # ret
			return 0x20444d41
		elif byte_code == \
			(b"\xB8\x02\x00\x00\x80",  # mov ax,0x80000002
			b"\x0f\xa2"                # cpuid
			b"\x89\xD8"                # mov ax,bx
			b"\xC3",):                 # ret
			return 0x657a7952
		elif byte_code == \
			(b"\xB8\x02\x00\x00\x80",  # mov ax,0x80000002
			b"\x0f\xa2"                # cpuid
			b"\x89\xC8"                # mov ax,cx
			b"\xC3",):                 # ret
			return 0x2037206e
		elif byte_code == \
			(b"\xB8\x02\x00\x00\x80",  # mov ax,0x80000002
			b"\x0f\xa2"                # cpuid
			b"\x89\xD0"                # mov ax,dx
			b"\xC3",):                 # ret
			return 0x30303732
		elif byte_code == \
			(b"\xB8\x03\x00\x00\x80",  # mov ax,0x80000003
			b"\x0f\xa2"                # cpuid
			b"\x89\xC0"                # mov ax,ax
			b"\xC3",):                 # ret
			return 0x69452058
		elif byte_code == \
			(b"\xB8\x03\x00\x00\x80",  # mov ax,0x80000003
			b"\x0f\xa2"                # cpuid
			b"\x89\xD8"                # mov ax,bx
			b"\xC3",):                 # ret
			return 0x2d746867
		elif byte_code == \
			(b"\xB8\x03\x00\x00\x80",  # mov ax,0x80000003
			b"\x0f\xa2"                # cpuid
			b"\x89\xC8"                # mov ax,cx
			b"\xC3",):                 # ret
			return 0x65726f43
		elif byte_code == \
			(b"\xB8\x03\x00\x00\x80",  # mov ax,0x80000003
			b"\x0f\xa2"                # cpuid
			b"\x89\xD0"                # mov ax,dx
			b"\xC3",):                 # ret
			return 0x6f725020
		elif byte_code == \
			(b"\xB8\x04\x00\x00\x80",  # mov ax,0x80000004
			b"\x0f\xa2"                # cpuid
			b"\x89\xC0"                # mov ax,ax
			b"\xC3",):                 # ret
			return 0x73736563
		elif byte_code == \
			(b"\xB8\x04\x00\x00\x80",  # mov ax,0x80000004
			b"\x0f\xa2"                # cpuid
			b"\x89\xD8"                # mov ax,bx
			b"\xC3",):                 # ret
			return 0x2020726f
		elif byte_code == \
			(b"\xB8\x04\x00\x00\x80",  # mov ax,0x80000004
			b"\x0f\xa2"                # cpuid
			b"\x89\xC8"                # mov ax,cx
			b"\xC3",):                 # ret
			return 0x20202020
		elif byte_code == \
			(b"\xB8\x04\x00\x00\x80",  # mov ax,0x80000004
			b"\x0f\xa2"                # cpuid
			b"\x89\xD0"                # mov ax,dx
			b"\xC3",):                 # ret
			return 0x202020

		raise Exception("Unexpected byte code")


class MockDataSource(object):
	bits = '64bit'
	cpu_count = 1
	is_windows = platform.system().lower() == 'windows'
	arch_string_raw = 'INVALID'
	uname_string_raw = 'INVALID'
	can_cpuid = True


class TestCPUID(unittest.TestCase):
	def setUp(self):
		helpers.backup_data_source(cpuinfo)
		helpers.monkey_patch_data_source(cpuinfo, MockDataSource)

	def tearDown(self):
		helpers.restore_data_source(cpuinfo)

	# Make sure this returns {} on an invalid arch
	def test_return_empty(self):
		self.assertEqual({}, cpuinfo._get_cpu_info_from_cpuid())

	def test_normal(self):
		cpuid = MockCPUID()
		print('cpuid', cpuid)
		self.assertIsNotNone(cpuid)

		self.assertFalse(cpuid.is_selinux_enforcing)

		max_extension_support = cpuid.get_max_extension_support()
		print('max_extension_support', hex(max_extension_support))
		self.assertEqual(0x8000001f, max_extension_support)

		cache_info = cpuid.get_cache(max_extension_support)
		print('cache_info', cache_info)
		self.assertEqual({'size_kb': 64, 'line_size_b': 6, 'associativity': 512}, cache_info)

		info = cpuid.get_info()
		print('info', info)
		self.assertEqual({'stepping': 2, 'model': 8, 'family': 15, 'processor_type': 0, 'extended_model': 0, 'extended_family': 8}, info)

		processor_brand = cpuid.get_processor_brand(max_extension_support)
		print('processor_brand', processor_brand)
		self.assertEqual("AMD Ryzen 7 2700X Eight-Core Processor", processor_brand)

		hz_actual = cpuid.get_raw_hz()
		print('hz_actual', hz_actual)
		self.assertEqual(3727888314, hz_actual)

		vendor_id = cpuid.get_vendor_id()
		print('vendor_id', vendor_id)
		self.assertEqual('AuthenticAMD', vendor_id)

		flags = cpuid.get_flags(max_extension_support)
		print('flags', flags)
		self.assertEqual(
		['3dnowprefetch', 'abm', 'adx', 'aes', 'apic', 'avx', 'avx2', 'bmi1',
		'bmi2', 'clflush', 'clflushopt', 'cmov', 'cmp_legacy', 'cr8_legacy',
		'cx16', 'cx8', 'dbx', 'de', 'extapic', 'f16c', 'fma', 'fpu', 'fxsr',
		'ht', 'lahf_lm', 'lm', 'mca', 'mce', 'misalignsse', 'mmx', 'monitor',
		'movbe', 'msr', 'mtrr', 'osvw', 'osxsave', 'pae', 'pat', 'pci_l2i',
		'pclmulqdq', 'perfctr_core', 'perfctr_nb', 'pge', 'pni', 'popcnt',
		'pse', 'pse36', 'rdrnd', 'rdseed', 'sep', 'sha', 'skinit', 'smap',
		'smep', 'sse', 'sse2', 'sse4_1', 'sse4_2', 'sse4a', 'ssse3', 'svm',
		'tce', 'topoext', 'tsc', 'vme', 'wdt', 'xsave'
		], flags)
