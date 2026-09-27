# [H] wifi: mt76: replace skb_put with skb_put_zero

## Summary
Severity: High
Advisory: CVE-2024-42225
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42225
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: replace skb_put with skb_put_zero

Avoid potentially reusing uninitialized data

## References
- https://git.kernel.org/stable/c/22ea2a7f0b64d323625950414a4496520fb33657
- https://git.kernel.org/stable/c/64f86337ccfe77fe3be5a9356b0dabde23fbb074
- https://git.kernel.org/stable/c/7f819a2f4fbc510e088b49c79addcf1734503578
- https://git.kernel.org/stable/c/dc7f14d00d0c4c21898f3504607f4a31079065a2
- https://git.kernel.org/stable/c/ff6b26be13032c5fbd6b6a0b24358f8eaac4f3af
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42225.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42225
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
