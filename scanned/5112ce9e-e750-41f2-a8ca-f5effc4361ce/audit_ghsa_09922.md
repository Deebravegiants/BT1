# [C] Decidim has a cross-site scripting (XSS) in user name

## Summary
Severity: Critical
Advisory: GHSA-fc46-r95f-hq7g
CVE: CVE-2026-23891
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-fc46-r95f-hq7g
Type: github-advisory

## Affected
- RubyGems: `decidim-core` — affected >=0.31.0.rc1 <0.31.1
- RubyGems: `decidim-core` — affected >=0 <0.30.5

## Details
### Impact
A stored code execution vulnerability in the user name field allows a low-privileged attacker to execute arbitrary code in the context of any user who passively visits a comment page, resulting in high confidentiality and integrity impact across security boundaries.

### Patches
N/A

### Workarounds
Not available

### References
OWASP ASVS v4.0.3-5.1.3

### Credits
This issue was discovered in a security audit organized by [octree](https://octree.ch/) and made by [Secu Labs](https://seculabs.ch/) against Decidim financed by the city of Lausanne (Switzerland).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-fc46-r95f-hq7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-23891
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/releases/tag/v0.30.5
- https://github.com/decidim/decidim/releases/tag/v0.31.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-core/CVE-2026-23891.yml
