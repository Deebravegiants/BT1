# [H] btrfs: don't check PageError in __extent_writepage

## Summary
Severity: High
Advisory: CVE-2023-53429
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53429
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: don't check PageError in __extent_writepage

__extent_writepage currenly sets PageError whenever any error happens,
and the also checks for PageError to decide if to call error handling.
This leads to very unclear responsibility for cleaning up on errors.
In the VM and generic writeback helpers the basic idea is that once
I/O is fired off all error handling responsibility is delegated to the
end I/O handler.  But if that end I/O handler sets the PageError bit,
and the submitter checks it, the bit could in some cases leak into the
submission context for fast enough I/O.

Fix this by simply not checking PageError and just using the local
ret variable to check for submission errors.  This also fundamentally
solves the long problem documented in a comment in __extent_writepage
by never leaking the error bit into the submission context.

## References
- https://git.kernel.org/stable/c/3e92499e3b004baffb479d61e191b41b604ece9a
- https://git.kernel.org/stable/c/d40be032ecd8ee1ca033bee43c7755d21fb4d72a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53429.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53429
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
