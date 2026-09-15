# [H] landlock: Handle weird files

## Summary
Severity: High
Advisory: CVE-2025-21830
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2025-21830
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

landlock: Handle weird files

A corrupted filesystem (e.g. bcachefs) might return weird files.
Instead of throwing a warning and allowing access to such file, treat
them as regular files.

## References
- https://git.kernel.org/stable/c/0fde195a373ab1267e60baa9e1a703a97e7464cd
- https://git.kernel.org/stable/c/2569e65d2eb6ac1afe6cb6dfae476afee8b6771a
- https://git.kernel.org/stable/c/39bb3d56f1c351e76bb18895d0e73796e653d5c1
- https://git.kernel.org/stable/c/49440290a0935f428a1e43a5ac8dc275a647ff80
- https://git.kernel.org/stable/c/7d6121228959ddf44a4b9b6a177384ac7854e2f9
- https://git.kernel.org/stable/c/a1fccf6b72b56343dd4f2d96b008147f9951eebd
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21830.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21830
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
