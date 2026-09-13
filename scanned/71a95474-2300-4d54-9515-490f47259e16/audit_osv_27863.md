# [H] netfilter: nf_tables: disallow anonymous set with timeout flag

## Summary
Severity: High
Advisory: CVE-2024-26642
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/CVE-2024-26642
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: disallow anonymous set with timeout flag

Anonymous sets are never used with timeout from userspace, reject this.
Exception to this rule is NFT_SET_EVAL to ensure legacy meters still work.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/16603605b667b70da974bea8216c93e7db043bf1
- https://git.kernel.org/stable/c/72c1efe3f247a581667b7d368fff3bd9a03cd57a
- https://git.kernel.org/stable/c/7cdc1be24cc1bcd56a3e89ac4aef20e31ad09199
- https://git.kernel.org/stable/c/8e07c16695583a66e81f67ce4c46e94dece47ba7
- https://git.kernel.org/stable/c/c0c2176d1814b92ea4c8e7eb7c9cd94cd99c1b12
- https://git.kernel.org/stable/c/e4988d8415bd0294d6f9f4a1e7095f8b50a97ca9
- https://git.kernel.org/stable/c/e9a0d3f376eb356d54ffce36e7cc37514cbfbd6f
- https://git.kernel.org/stable/c/fe40ffbca19dc70d7c6b1e3c77b9ccb404c57351
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26642.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26642
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
