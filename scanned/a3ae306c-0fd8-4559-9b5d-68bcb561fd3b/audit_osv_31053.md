# [M] arm64: ptrace: fix partial SETREGSET for NT_ARM_TAGGED_ADDR_CTRL

## Summary
Severity: Medium
Advisory: CVE-2024-57874
Ecosystem: Linux
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57874
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: ptrace: fix partial SETREGSET for NT_ARM_TAGGED_ADDR_CTRL

Currently tagged_addr_ctrl_set() doesn't initialize the temporary 'ctrl'
variable, and a SETREGSET call with a length of zero will leave this
uninitialized. Consequently tagged_addr_ctrl_set() will consume an
arbitrary value, potentially leaking up to 64 bits of memory from the
kernel stack. The read is limited to a specific slot on the stack, and
the issue does not provide a write mechanism.

As set_tagged_addr_ctrl() only accepts values where bits [63:4] zero and
rejects other values, a partial SETREGSET attempt will randomly succeed
or fail depending on the value of the uninitialized value, and the
exposure is significantly limited.

Fix this by initializing the temporary value before copying the regset
from userspace, as for other regsets (e.g. NT_PRSTATUS, NT_PRFPREG,
NT_ARM_SYSTEM_CALL). In the case of a zero-length write, the existing
value of the tagged address ctrl will be retained.

The NT_ARM_TAGGED_ADDR_CTRL regset is only visible in the
user_aarch64_view used by a native AArch64 task to manipulate another
native AArch64 task. As get_tagged_addr_ctrl() only returns an error
value when called for a compat task, tagged_addr_ctrl_get() and
tagged_addr_ctrl_set() should never observe an error value from
get_tagged_addr_ctrl(). Add a WARN_ON_ONCE() to both to indicate that
such an error would be unexpected, and error handlnig is not missing in
either case.

## References
- https://git.kernel.org/stable/c/1152dd13845efde5554f80c7e1233bae1d26bd3e
- https://git.kernel.org/stable/c/1370cf3eb5495d70e00547598583a4cd45b40b99
- https://git.kernel.org/stable/c/1c176f5155ee6161fee6f416b64aa50394d3f220
- https://git.kernel.org/stable/c/96035c0093db258975b8887676afe59a64c34a72
- https://git.kernel.org/stable/c/abd614bbfcee73247495bd9472da8f85ac83546e
- https://git.kernel.org/stable/c/ca62d90085f4af36de745883faab9f8a7cbb45d3
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57874.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57874
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
