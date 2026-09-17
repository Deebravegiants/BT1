# [H] cifs: fix potential double free during failed mount

## Summary
Severity: High
Advisory: CVE-2022-49541
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49541
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix potential double free during failed mount

RHBZ: https://bugzilla.redhat.com/show_bug.cgi?id=2088799

## References
- https://git.kernel.org/stable/c/8378a51e3f8140f60901fb27208cc7a6e47047b5
- https://git.kernel.org/stable/c/9a167fc440e5693c1cdd7f07071e05658bd9d89d
- https://git.kernel.org/stable/c/ce0008a0e410cdd95f0d8cd81b2902ec10a660c4
- https://git.kernel.org/stable/c/ee71f8f1cd3c8c4a251fd3e8abc89215ae3457cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49541.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49541
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
