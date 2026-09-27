# [M] arm64: ptrace: fix partial SETREGSET for NT_ARM_POE

## Summary
Severity: Medium
Advisory: CVE-2024-57877
Ecosystem: Linux
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57877
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: ptrace: fix partial SETREGSET for NT_ARM_POE

Currently poe_set() doesn't initialize the temporary 'ctrl' variable,
and a SETREGSET call with a length of zero will leave this
uninitialized. Consequently an arbitrary value will be written back to
target->thread.por_el0, potentially leaking up to 64 bits of memory from
the kernel stack. The read is limited to a specific slot on the stack,
and the issue does not provide a write mechanism.

Fix this by initializing the temporary value before copying the regset
from userspace, as for other regsets (e.g. NT_PRSTATUS, NT_PRFPREG,
NT_ARM_SYSTEM_CALL). In the case of a zero-length write, the existing
contents of POR_EL1 will be retained.

Before this patch:

| # ./poe-test
| Attempting to write NT_ARM_POE::por_el0 = 0x900d900d900d900d
| SETREGSET(nt=0x40f, len=8) wrote 8 bytes
|
| Attempting to read NT_ARM_POE::por_el0
| GETREGSET(nt=0x40f, len=8) read 8 bytes
| Read NT_ARM_POE::por_el0 = 0x900d900d900d900d
|
| Attempting to write NT_ARM_POE (zero length)
| SETREGSET(nt=0x40f, len=0) wrote 0 bytes
|
| Attempting to read NT_ARM_POE::por_el0
| GETREGSET(nt=0x40f, len=8) read 8 bytes
| Read NT_ARM_POE::por_el0 = 0xffff8000839c3d50

After this patch:

| # ./poe-test
| Attempting to write NT_ARM_POE::por_el0 = 0x900d900d900d900d
| SETREGSET(nt=0x40f, len=8) wrote 8 bytes
|
| Attempting to read NT_ARM_POE::por_el0
| GETREGSET(nt=0x40f, len=8) read 8 bytes
| Read NT_ARM_POE::por_el0 = 0x900d900d900d900d
|
| Attempting to write NT_ARM_POE (zero length)
| SETREGSET(nt=0x40f, len=0) wrote 0 bytes
|
| Attempting to read NT_ARM_POE::por_el0
| GETREGSET(nt=0x40f, len=8) read 8 bytes
| Read NT_ARM_POE::por_el0 = 0x900d900d900d900d

## References
- https://git.kernel.org/stable/c/4105dd76bc8ad6529d47157ef0565cb84ca6676c
- https://git.kernel.org/stable/c/594bfc4947c4fcabba1318d8384c61a29a6b89fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57877.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57877
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
