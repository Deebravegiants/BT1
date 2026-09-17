# [C] Cockpit is vulnerable to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-fm6c-rhcf-7439
CVE: CVE-2026-38992
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-fm6c-rhcf-7439
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.14.0

## Details
Cockpit versions 2.13.5 and earlier are vulnerable to arbitrary code execution via the filter parameter within multiple endpoints. This vulnerability allows an attacker to run system commands on the underlying infrastructure via the MongoLite $func operator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38992
- https://felsec.com/posts/cockpit-cms-2.13.5-multi-vulns
- https://github.com/Cockpit-HQ/Cockpit
- https://github.com/Cockpit-HQ/Cockpit/releases/tag/2.14.0
