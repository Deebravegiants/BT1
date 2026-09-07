# [M] Decidim Cross-site Scripting vulnerability in the external link redirections

## Summary
Severity: Medium
Advisory: GHSA-469h-mqg8-535r
CVE: CVE-2023-32693
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-11
Source: https://github.com/advisories/GHSA-469h-mqg8-535r
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0.25.0 <0.26.7
- RubyGems: `decidim-core` — affected >=0.27.0 <0.27.3
- RubyGems: `decidim-core` — affected >=0.25.0 <0.26.7
- RubyGems: `decidim` — affected >=0.27.0 <0.27.3

## Details
### Impact

The external link feature is susceptible to Cross-site scripting. This allows a remote attacker to execute JavaScript code in the context of a currently logged-in user. An attacker could use this vulnerability to make other users endorse or support proposals they have no intention of supporting or endorsing.

### Patches

The problem was patched in [v0.27.3](https://github.com/decidim/decidim/releases/tag/v0.27.3) and [v0.26.7](https://github.com/decidim/decidim/releases/tag/v0.26.7)

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-469h-mqg8-535r
- https://nvd.nist.gov/vuln/detail/CVE-2023-32693
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/releases/tag/v0.26.7
- https://github.com/decidim/decidim/releases/tag/v0.27.3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-core/CVE-2023-32693.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim/CVE-2023-32693.yml
