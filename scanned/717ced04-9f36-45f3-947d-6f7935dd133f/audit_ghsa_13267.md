# [H] Decidim Cross-site Scripting vulnerability in the processes filter

## Summary
Severity: High
Advisory: GHSA-5652-92r9-3fx9
CVE: CVE-2023-34089
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-11
Source: https://github.com/advisories/GHSA-5652-92r9-3fx9
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0.14.0 <0.26.7
- RubyGems: `decidim` — affected >=0.27.0 <0.27.3
- RubyGems: `decidim-core` — affected >=0.14.0 <0.26.7
- RubyGems: `decidim-core` — affected >=0.27.0 <0.27.3

## Details
### Impact

The processes filter feature is susceptible to Cross-site scripting. This allows a remote attacker to execute JavaScript code in the context of a currently logged-in user. An attacker could use this vulnerability to make other users endorse or support proposals they have no intention of supporting or endorsing.

### Patches

The problem was patched in [v0.27.3](https://github.com/decidim/decidim/releases/tag/v0.27.3) and [v0.26.7](https://github.com/decidim/decidim/releases/tag/v0.26.7)

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-5652-92r9-3fx9
- https://nvd.nist.gov/vuln/detail/CVE-2023-34089
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/releases/tag/v0.26.6
- https://github.com/decidim/decidim/releases/tag/v0.26.7
- https://github.com/decidim/decidim/releases/tag/v0.27.3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-core/CVE-2023-34089.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim/CVE-2023-34089.yml
