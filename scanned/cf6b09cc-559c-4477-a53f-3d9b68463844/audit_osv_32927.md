# [H] wifi: mt76: mt7996: drop fragments with multicast or broadcast RA

## Summary
Severity: High
Advisory: CVE-2025-38343
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38343
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7996: drop fragments with multicast or broadcast RA

IEEE 802.11 fragmentation can only be applied to unicast frames.
Therefore, drop fragments with multicast or broadcast RA. This patch
addresses vulnerabilities such as CVE-2020-26145.

## References
- https://git.kernel.org/stable/c/24900688ee47071aa6a61e78473999b5b80f0423
- https://git.kernel.org/stable/c/5fd5b8132b5de08c99eea003f7715ff2e361b007
- https://git.kernel.org/stable/c/80fda1cd7b0a1edd0849dc71403a070d0922118d
- https://git.kernel.org/stable/c/d4b93f9c2f666011dcf810050ef60a6b8d06f186
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38343.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38343
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
