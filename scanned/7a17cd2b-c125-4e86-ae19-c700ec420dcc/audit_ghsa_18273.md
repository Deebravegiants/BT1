# [M] YesWiki Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-29cj-cxw4-v4j2
CVE: CVE-2025-52277
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-29cj-cxw4-v4j2
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0

## Details
Cross Site Scripting vulnerability in YesWiki v.4.5.4 allows a remote attacker to execute arbitrary code via a crafted payload to the meta configuration robots field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52277
- https://github.com/YesWiki/yeswiki
- https://github.com/nakkouchtarek/CVE/tree/main/CVE-2025-52277
- http://yeswiki.com
