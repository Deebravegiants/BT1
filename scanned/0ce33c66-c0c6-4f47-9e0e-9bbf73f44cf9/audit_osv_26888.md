# [H] crypto: qat - fix out-of-bounds read

## Summary
Severity: High
Advisory: CVE-2023-54325
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54325
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat - fix out-of-bounds read

When preparing an AER-CTR request, the driver copies the key provided by
the user into a data structure that is accessible by the firmware.
If the target device is QAT GEN4, the key size is rounded up by 16 since
a rounded up size is expected by the device.
If the key size is rounded up before the copy, the size used for copying
the key might be bigger than the size of the region containing the key,
causing an out-of-bounds read.

Fix by doing the copy first and then update the keylen.

This is to fix the following warning reported by KASAN:

	[  138.150574] BUG: KASAN: global-out-of-bounds in qat_alg_skcipher_init_com.isra.0+0x197/0x250 [intel_qat]
	[  138.150641] Read of size 32 at addr ffffffff88c402c0 by task cryptomgr_test/2340

	[  138.150651] CPU: 15 PID: 2340 Comm: cryptomgr_test Not tainted 6.2.0-rc1+ #45
	[  138.150659] Hardware name: Intel Corporation ArcherCity/ArcherCity, BIOS EGSDCRB1.86B.0087.D13.2208261706 08/26/2022
	[  138.150663] Call Trace:
	[  138.150668]  <TASK>
	[  138.150922]  kasan_check_range+0x13a/0x1c0
	[  138.150931]  memcpy+0x1f/0x60
	[  138.150940]  qat_alg_skcipher_init_com.isra.0+0x197/0x250 [intel_qat]
	[  138.151006]  qat_alg_skcipher_init_sessions+0xc1/0x240 [intel_qat]
	[  138.151073]  crypto_skcipher_setkey+0x82/0x160
	[  138.151085]  ? prepare_keybuf+0xa2/0xd0
	[  138.151095]  test_skcipher_vec_cfg+0x2b8/0x800

## References
- https://git.kernel.org/stable/c/2b1501f058245573a3aa6bf234d205dde1196184
- https://git.kernel.org/stable/c/7697139d5dfd491f4c495a914a1dd68f6e827a0f
- https://git.kernel.org/stable/c/dc3809f390357c8992f0a23083da934a20fef9af
- https://git.kernel.org/stable/c/f6044cc3030e139f60c281386f28bda6e3049d66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54325.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54325
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
