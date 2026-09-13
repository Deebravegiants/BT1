# [M] arm64: kexec: initialize kexec_buf struct in load_other_segments()

## Summary
Severity: Medium
Advisory: CVE-2025-39904
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39904
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: kexec: initialize kexec_buf struct in load_other_segments()

Patch series "kexec: Fix invalid field access".

The kexec_buf structure was previously declared without initialization. 
commit bf454ec31add ("kexec_file: allow to place kexec_buf randomly")
added a field that is always read but not consistently populated by all
architectures.  This un-initialized field will contain garbage.

This is also triggering a UBSAN warning when the uninitialized data was
accessed:

	------------[ cut here ]------------
	UBSAN: invalid-load in ./include/linux/kexec.h:210:10
	load of value 252 is not a valid value for type '_Bool'

Zero-initializing kexec_buf at declaration ensures all fields are cleanly
set, preventing future instances of uninitialized memory being used.

An initial fix was already landed for arm64[0], and this patchset fixes
the problem on the remaining arm64 code and on riscv, as raised by Mark.

Discussions about this problem could be found at[1][2].


This patch (of 3):

The kexec_buf structure was previously declared without initialization.
commit bf454ec31add ("kexec_file: allow to place kexec_buf randomly")
added a field that is always read but not consistently populated by all
architectures. This un-initialized field will contain garbage.

This is also triggering a UBSAN warning when the uninitialized data was
accessed:

	------------[ cut here ]------------
	UBSAN: invalid-load in ./include/linux/kexec.h:210:10
	load of value 252 is not a valid value for type '_Bool'

Zero-initializing kexec_buf at declaration ensures all fields are
cleanly set, preventing future instances of uninitialized memory being
used.

## References
- https://git.kernel.org/stable/c/04d3cd43700a2d0fe4bfb1012a8ec7f2e34a3507
- https://git.kernel.org/stable/c/340cc9a3bd30b25edaf6a9708d41b5f2c10a054a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39904.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39904
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
