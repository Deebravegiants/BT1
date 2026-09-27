# [H] staging: rtl8192u: Fix use after free in ieee80211_rx()

## Summary
Severity: High
Advisory: CVE-2022-50732
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50732
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8192u: Fix use after free in ieee80211_rx()

We cannot dereference the "skb" pointer after calling
ieee80211_monitor_rx(), because it is a use after free.

## References
- https://git.kernel.org/stable/c/288ada16a93aab5aa2ebea8190aafdb35b716854
- https://git.kernel.org/stable/c/73df1172bbcc8d45cd28e3b1a9ca2edb2f9f7ce6
- https://git.kernel.org/stable/c/9c03db0ec84b7964a11b20706665c99a5fead332
- https://git.kernel.org/stable/c/a0df8d44b555ae09729d6533fd4532977563c7b9
- https://git.kernel.org/stable/c/b0aaec894a909c88117c8bda6c7c9b26cf7c744b
- https://git.kernel.org/stable/c/bcc5e2dcf09089b337b76fc1a589f6ff95ca19ac
- https://git.kernel.org/stable/c/daa8045a991363ccdae5615d170f35aa1135e7a7
- https://git.kernel.org/stable/c/de174163c0d319ff06d622e79130a0017c8f5a6e
- https://git.kernel.org/stable/c/fdc62d31d50e4ce5d8f363fcb8299ba0e00ee6fd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50732.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50732
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
