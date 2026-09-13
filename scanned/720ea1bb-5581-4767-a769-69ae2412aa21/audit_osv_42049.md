# [H] ksmbd: prevent path traversal bypass by restricting caseless retry

## Summary
Severity: High
Advisory: CVE-2026-64400
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64400
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: prevent path traversal bypass by restricting caseless retry

ksmbd_vfs_path_lookup() enforces LOOKUP_BENEATH to restrict path
resolution within the share root. When a crafted path attempts to
escape the share boundary using parent-directory components ('..'),
vfs_path_parent_lookup() detects this and immediately fails,
returning -EXDEV.

However, a bug exists in __ksmbd_vfs_kern_path() under caseless mode.
The function fails to intercept the -EXDEV error and erroneously
falls through to the caseless retry logic, which is intended only
for genuinely missing files. During this retry process, the path
is reconstructed, leading to an unintended LOOKUP_BENEATH bypass
that allows write-capable users to create zero-length files or
directories outside the exported share.

Fix this by ensuring that the execution only proceeds to the caseless
lookup retry when the error is specifically -ENOENT. Any other errors,
such as -EXDEV from a path traversal attempt, must be returned immediately.

## References
- https://git.kernel.org/stable/c/54bab9ba5a9f156ffa9324fcbe5a356fd0242f95
- https://git.kernel.org/stable/c/8c9a4f1327eb71efbf14842e7b8a6d965077eb67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64400.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64400
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
