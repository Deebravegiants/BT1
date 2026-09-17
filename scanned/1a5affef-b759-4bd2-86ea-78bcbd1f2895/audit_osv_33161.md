# [H] smb: client: fix race with concurrent opens in rename(2)

## Summary
Severity: High
Advisory: CVE-2025-39825
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39825
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.150, >=6.2.0 <6.6.104, >=6.7.0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix race with concurrent opens in rename(2)

Besides sending the rename request to the server, the rename process
also involves closing any deferred close, waiting for outstanding I/O
to complete as well as marking all existing open handles as deleted to
prevent them from deferring closes, which increases the race window
for potential concurrent opens on the target file.

Fix this by unhashing the dentry in advance to prevent any concurrent
opens on the target.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/24b9ed739c8c5b464d983e12cf308982f3ae93c2
- https://git.kernel.org/stable/c/289f945acb20b9b54fe4d13895e44aa58965ddb2
- https://git.kernel.org/stable/c/c9991af5e09924f6f3b3e6996a5e09f9504b4358
- https://git.kernel.org/stable/c/c9e7de284da0be5b44dbe79d71573f9f7f9b144c
- https://git.kernel.org/stable/c/d84291fc7453df7881a970716f8256273aca5747
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39825.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39825
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
