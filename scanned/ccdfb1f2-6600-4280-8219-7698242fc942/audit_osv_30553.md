# [C] NFSD: Prevent a potential integer overflow

## Summary
Severity: Critical
Advisory: CVE-2024-53146
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53146
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Prevent a potential integer overflow

If the tag length is >= U32_MAX - 3 then the "length + 4" addition
can result in an integer overflow. Address this by splitting the
decoding into several steps so that decode_cb_compound4res() does
not have to perform arithmetic on the unsafe length value.

## References
- https://git.kernel.org/stable/c/084f797dbc7e52209a4ab6dbc7f0109268754eb9
- https://git.kernel.org/stable/c/3c5f545c9a1f8a1869246f6f3ae8c17289d6a841
- https://git.kernel.org/stable/c/745f7ce5a95e783ba62fe774325829466aec2aa8
- https://git.kernel.org/stable/c/7f33b92e5b18e904a481e6e208486da43e4dc841
- https://git.kernel.org/stable/c/842f1c27a1aef5367e535f9e85c8c3b06352151a
- https://git.kernel.org/stable/c/90adbae9dd158da8331d9fdd32077bd1af04f553
- https://git.kernel.org/stable/c/ccd3394f9a7200d6b088553bf38e688620cd27af
- https://git.kernel.org/stable/c/dde654cad08fdaac370febb161ec41eb58e9d2a2
- https://git.kernel.org/stable/c/de53c5305184ca1333b87e695d329d1502d694ce
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53146.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53146
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
