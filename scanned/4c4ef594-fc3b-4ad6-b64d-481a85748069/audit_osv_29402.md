# [H] mISDN: Fix a use after free in hfcmulti_tx()

## Summary
Severity: High
Advisory: CVE-2024-42280
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42280
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mISDN: Fix a use after free in hfcmulti_tx()

Don't dereference *sp after calling dev_kfree_skb(*sp).

## References
- https://git.kernel.org/stable/c/4d8b642985ae24f4b3656438eb8489834a17bb80
- https://git.kernel.org/stable/c/61ab751451f5ebd0b98e02276a44e23a10110402
- https://git.kernel.org/stable/c/70db2c84631f50e02e6b32b543700699dd395803
- https://git.kernel.org/stable/c/7e4a539bca7d8d20f2c5d93c18cce8ef77cd78e0
- https://git.kernel.org/stable/c/8f4030277dfb9dbe04fd78566b19931097c9d629
- https://git.kernel.org/stable/c/9460ac3dd1ae033bc2b021a458fb535a0c36ddb2
- https://git.kernel.org/stable/c/d3e4d4a98c5629ccdcb762a0ff6c82ba9738a0c3
- https://git.kernel.org/stable/c/ddc79556641ee070d36be0de4a1f0a16a71f1fc7
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42280.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
