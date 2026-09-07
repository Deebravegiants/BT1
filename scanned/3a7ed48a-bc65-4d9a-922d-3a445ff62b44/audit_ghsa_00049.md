# [M] Radiant CMS vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-mvw8-v767-qhjm
CVE: CVE-2018-5216
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-01-06
Source: https://github.com/advisories/GHSA-mvw8-v767-qhjm
Type: github-advisory

## Affected
- RubyGems: `radiant` — affected >=0

## Details
Radiant CMS 1.1.4 has XSS via crafted Markdown input in the `part_body_content` parameter to an `admin/pages/*/edit `resource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5216
- https://github.com/imsebao/404team
- https://github.com/imsebao/404team/blob/master/radiantcms.md
