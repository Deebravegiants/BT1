# [M] Rails Active Storage has possible glob injection in its DiskService

## Summary
Severity: Medium
Advisory: GHSA-73f9-jhhh-hr5m
CVE: CVE-2026-33202
CWE: CWE-74
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-73f9-jhhh-hr5m
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=8.1.0.beta1 <8.1.2.1
- RubyGems: `activestorage` — affected >=8.0.0.beta1 <8.0.4.1
- RubyGems: `activestorage` — affected >=0 <7.2.3.1

## Details
### Impact
Active Storage's `DiskService#delete_prefixed` passes blob keys directly to `Dir.glob` without escaping glob metacharacters. If a blob key contains attacker-controlled input or custom-generated keys with glob metacharacters, it may be possible to delete unintended files from the storage directory.

### Releases
The fixed releases are available at the normal locations.

## References
- https://github.com/rails/rails/security/advisories/GHSA-73f9-jhhh-hr5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33202
- https://github.com/rails/rails/commit/8c9676b803820110548cdb7523800db43bc6874c
- https://github.com/rails/rails/commit/955284d26e469a9c026a4eee5b21f0414ab0bccf
- https://github.com/rails/rails/commit/fa19073546360856e9f4dab221fc2c5d73a45e82
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.2.3.1
- https://github.com/rails/rails/releases/tag/v8.0.4.1
- https://github.com/rails/rails/releases/tag/v8.1.2.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activestorage/CVE-2026-33202.yml
