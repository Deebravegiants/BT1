# [H] Decidim has broken access control in templates

## Summary
Severity: High
Advisory: GHSA-639h-86hw-qcjq
CVE: CVE-2023-36465
CWE: CWE-284, CWE-732
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2023-10-05
Source: https://github.com/advisories/GHSA-639h-86hw-qcjq
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0.23.2 <0.26.8
- RubyGems: `decidim-templates` — affected >=0.23.2 <0.26.8
- RubyGems: `decidim-templates` — affected >=0.27.0 <0.27.4
- RubyGems: `decidim` — affected >=0.27.0 <0.27.4

## Details
### Impact

The `templates` module doesn't enforce the correct permissions, allowing any logged-in user to access to this functionality in the administration panel. An attacker could use this vulnerability to change, create or delete templates of surveys.

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-639h-86hw-qcjq
- https://nvd.nist.gov/vuln/detail/CVE-2023-36465
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/releases/tag/v0.26.8
- https://github.com/decidim/decidim/releases/tag/v0.27.4
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-templates/CVE-2023-36465.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim/CVE-2023-36465.yml
