# [M] NamelessMC allows sensitive information disclosure in member list component

## Summary
Severity: Medium
Advisory: CVE-2025-54118
Aliases: GHSA-cj37-8jqc-hv2w
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-08-18
Source: https://osv.dev/vulnerability/CVE-2025-54118
Type: osv

## Details
NamelessMC is a free, easy to use & powerful website software for Minecraft servers. Sensitive information disclosure in NamelessMC before 2.2.4 allows unauthenticated remote attacker to gain sensitive information such as absolute path of the source code via list parameter. This vulnerability is fixed in 2.2.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54118.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-cj37-8jqc-hv2w
- https://nvd.nist.gov/vuln/detail/CVE-2025-54118
- https://github.com/NamelessMC/Nameless/commit/3b94eb594dcbb1abc5524e41a0631df3ac95de8f
