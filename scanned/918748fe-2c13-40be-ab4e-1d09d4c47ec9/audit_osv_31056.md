# [M] arm64: ptrace: fix partial SETREGSET for NT_ARM_FPMR

## Summary
Severity: Medium
Advisory: CVE-2024-57878
Ecosystem: Linux
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57878
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: ptrace: fix partial SETREGSET for NT_ARM_FPMR

Currently fpmr_set() doesn't initialize the temporary 'fpmr' variable,
and a SETREGSET call with a length of zero will leave this
uninitialized. Consequently an arbitrary value will be written back to
target->thread.uw.fpmr, potentially leaking up to 64 bits of memory from
the kernel stack. The read is limited to a specific slot on the stack,
and the issue does not provide a write mechanism.

Fix this by initializing the temporary value before copying the regset
from userspace, as for other regsets (e.g. NT_PRSTATUS, NT_PRFPREG,
NT_ARM_SYSTEM_CALL). In the case of a zero-length write, the existing
contents of FPMR will be retained.

Before this patch:

| # ./fpmr-test
| Attempting to write NT_ARM_FPMR::fpmr = 0x900d900d900d900d
| SETREGSET(nt=0x40e, len=8) wrote 8 bytes
|
| Attempting to read NT_ARM_FPMR::fpmr
| GETREGSET(nt=0x40e, len=8) read 8 bytes
| Read NT_ARM_FPMR::fpmr = 0x900d900d900d900d
|
| Attempting to write NT_ARM_FPMR (zero length)
| SETREGSET(nt=0x40e, len=0) wrote 0 bytes
|
| Attempting to read NT_ARM_FPMR::fpmr
| GETREGSET(nt=0x40e, len=8) read 8 bytes
| Read NT_ARM_FPMR::fpmr = 0xffff800083963d50

After this patch:

| # ./fpmr-test
| Attempting to write NT_ARM_FPMR::fpmr = 0x900d900d900d900d
| SETREGSET(nt=0x40e, len=8) wrote 8 bytes
|
| Attempting to read NT_ARM_FPMR::fpmr
| GETREGSET(nt=0x40e, len=8) read 8 bytes
| Read NT_ARM_FPMR::fpmr = 0x900d900d900d900d
|
| Attempting to write NT_ARM_FPMR (zero length)
| SETREGSET(nt=0x40e, len=0) wrote 0 bytes
|
| Attempting to read NT_ARM_FPMR::fpmr
| GETREGSET(nt=0x40e, len=8) read 8 bytes
| Read NT_ARM_FPMR::fpmr = 0x900d900d900d900d

## References
- https://git.kernel.org/stable/c/8ab73c34e3c5b580721696665eabd799346bc50b
- https://git.kernel.org/stable/c/f5d71291841aecfe5d8435da2dfa7f58ccd18bc8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57878.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57878
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
