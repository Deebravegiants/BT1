# [C] fs/ntfs3: add depth limit to indx_find_buffer to prevent stack overflow

## Summary
Severity: Critical
Advisory: CVE-2026-72194
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72194
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: add depth limit to indx_find_buffer to prevent stack overflow

indx_find_buffer() recursively descends the B+ tree index with no depth
limit.  A crafted NTFS image with circular index node references causes
unbounded recursion, overflowing the kernel stack and panicking the
system.

This is reachable by mounting a malicious NTFS filesystem (e.g. from a
USB drive via desktop automount) and deleting a file whose index entry
triggers the rebalancing fallback path in indx_delete_entry().

Add a depth parameter and bail out with -EINVAL when it reaches the
fnd->nodes array bound, matching the constraint already enforced by
fnd_push() in indx_find().

The related function indx_find() was previously patched for a similar
infinite-loop issue (commit 1732053c8a6b), but indx_find_buffer() was
missed.

## References
- https://git.kernel.org/stable/c/1ebd684b8f627f75bc3e03f8b2ad8400fd1f02cd
- https://git.kernel.org/stable/c/65357a81f64cb3fbe13b4b937586755e4b3a072f
- https://git.kernel.org/stable/c/78612f478f9fadcec4f9b3b089970da67ffb47e9
- https://git.kernel.org/stable/c/908c9243ba309997b73cbda3e4c563d0fb345ee9
- https://git.kernel.org/stable/c/96fb64f9da86fd2dbd78fbe9d9e41ae27e12ce34
- https://git.kernel.org/stable/c/99031d4f63c785d2a985b6a4c64c4256f7117052
- https://git.kernel.org/stable/c/fdf50c788e0991e42a187ff75479a0df7fb752f1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72194.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72194
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
