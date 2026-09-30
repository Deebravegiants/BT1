# [M] fs/ntfs3: Fix possible deadlock in mi_read

## Summary
Severity: Medium
Advisory: CVE-2024-50245
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50245
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Fix possible deadlock in mi_read

Mutex lock with another subclass used in ni_lock_dir().

## References
- https://git.kernel.org/stable/c/03b097099eef255fbf85ea6a786ae3c91b11f041
- https://git.kernel.org/stable/c/34e3220efd666d49965a26840d39f27601ce70f4
- https://git.kernel.org/stable/c/47e8a17491e37df53743bc2e72309f8f0d6224af
- https://git.kernel.org/stable/c/c8e7d3b72ee57e43d58ba560fe7970dd840a4061
- https://git.kernel.org/stable/c/f1bc362fe978952a9304bd0286788b0ae7724f14
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50245.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50245
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
