# [M] Cross-site Scripting in LaraCMS

## Summary
Severity: Medium
Advisory: GHSA-m72g-42q6-gvc2
CVE: CVE-2020-20129
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-04
Source: https://github.com/advisories/GHSA-m72g-42q6-gvc2
Type: github-advisory

## Affected
- Packagist: `wanglelecc/laracms` — affected >=0

## Details
LaraCMS contains a stored cross-site scripting (XSS) vulnerability which allows attackers to execute arbitrary web scripts or HTML via a crafted payload in the content editor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-20129
- https://github.com/wanglelecc/laracms/issues/34
- https://github.com/wanglelecc/laracms
