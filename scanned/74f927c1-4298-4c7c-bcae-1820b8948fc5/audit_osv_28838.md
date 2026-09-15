# [M] wifi: nl80211: don't free NULL coalescing rule

## Summary
Severity: Medium
Advisory: CVE-2024-36941
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36941
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: nl80211: don't free NULL coalescing rule

If the parsing fails, we can dereference a NULL pointer here.

## References
- https://git.kernel.org/stable/c/244822c09b4f9aedfb5977f03c0deeb39da8ec7d
- https://git.kernel.org/stable/c/327382dc0f16b268950b96e0052595efd80f7b0a
- https://git.kernel.org/stable/c/5a730a161ac2290d46d49be76b2b1aee8d2eb307
- https://git.kernel.org/stable/c/801ea33ae82d6a9d954074fbcf8ea9d18f1543a7
- https://git.kernel.org/stable/c/97792d0611ae2e6fe3ccefb0a94a1d802317c457
- https://git.kernel.org/stable/c/ad12c74e953b68ad85c78adc6408ed8435c64af4
- https://git.kernel.org/stable/c/b0db4caa10f2e4e811cf88744fbf0d074b67ec1f
- https://git.kernel.org/stable/c/f92772a642485394db5c9a17bd0ee73fc6902383
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36941.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36941
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
