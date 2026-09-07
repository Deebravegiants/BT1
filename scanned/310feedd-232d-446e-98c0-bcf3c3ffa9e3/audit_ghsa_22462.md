# [M] Cross-site Scripting in ZKEACMS

## Summary
Severity: Medium
Advisory: GHSA-hc72-vj3g-5g2g
CVE: CVE-2022-29362
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-26
Source: https://github.com/advisories/GHSA-hc72-vj3g-5g2g
Type: github-advisory

## Affected
- NuGet: `ZKEACMS.Publisher` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in /navigation/create?ParentID=%23 of ZKEACMS v3.5.2 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the ParentID parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29362
- https://github.com/SeriaWei/ZKEACMS/issues/457
- https://github.com/SeriaWei/ZKEACMS/commit/833c5460dc5c6152092f6ad54b8b832870a59903
- https://github.com/SeriaWei/ZKEACMS
