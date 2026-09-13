# [H] rtnetlink: make sure to refresh master_dev/m_ops in __rtnl_newlink()

## Summary
Severity: High
Advisory: CVE-2022-48742
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48742
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <4.9.300, >=4.10.0 <4.14.265, >=4.15.0 <4.19.228, >=4.20.0 <5.4.177, >=5.5.0 <5.10.97, >=5.11.0 <5.15.20, >=5.16.0 <5.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtnetlink: make sure to refresh master_dev/m_ops in __rtnl_newlink()

While looking at one unrelated syzbot bug, I found the replay logic
in __rtnl_newlink() to potentially trigger use-after-free.

It is better to clear master_dev and m_ops inside the loop,
in case we have to replay it.

## References
- https://git.kernel.org/stable/c/2cf180360d66bd657e606c1217e0e668e6faa303
- https://git.kernel.org/stable/c/36a9a0aee881940476b254e0352581401b23f210
- https://git.kernel.org/stable/c/3bbe2019dd12b8d13671ee6cda055d49637b4c39
- https://git.kernel.org/stable/c/7d9211678c0f0624f74cdff36117ab8316697bb8
- https://git.kernel.org/stable/c/a01e60a1ec6bef9be471fb7182a33c6d6f124e93
- https://git.kernel.org/stable/c/bd43771ee9759dd9dfae946bff190e2c5a120de5
- https://git.kernel.org/stable/c/c6f6f2444bdbe0079e41914a35081530d0409963
- https://git.kernel.org/stable/c/def5e7070079b2a214b3b1a2fbec623e6fbfe34a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48742.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48742
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
