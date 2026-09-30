# [H] f2fs: explicitly null-terminate the xattr list

## Summary
Severity: High
Advisory: CVE-2023-52436
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2023-52436
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.19.306, >=4.20.0 <5.4.268, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.74, >=6.2.0 <6.6.13, >=6.7.0 <6.7.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: explicitly null-terminate the xattr list

When setting an xattr, explicitly null-terminate the xattr list.  This
eliminates the fragile assumption that the unused xattr space is always
zeroed.

## References
- https://git.kernel.org/stable/c/12cf91e23b126718a96b914f949f2cdfeadc7b2a
- https://git.kernel.org/stable/c/16ae3132ff7746894894927c1892493693b89135
- https://git.kernel.org/stable/c/2525d1ba225b5c167162fa344013c408e8b4de36
- https://git.kernel.org/stable/c/32a6cfc67675ee96fe107aeed5af9776fec63f11
- https://git.kernel.org/stable/c/3e47740091b05ac8d7836a33afd8646b6863ca52
- https://git.kernel.org/stable/c/5de9e9dd1828db9b8b962f7ca42548bd596deb8a
- https://git.kernel.org/stable/c/e26b6d39270f5eab0087453d9b544189a38c8564
- https://git.kernel.org/stable/c/f6c30bfe5a49bc38cae985083a11016800708fea
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52436.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52436
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
