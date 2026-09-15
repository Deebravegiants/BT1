# [M] Rails Active Support has a possible ReDoS vulnerability in number_to_delimited

## Summary
Severity: Medium
Advisory: GHSA-cg4j-q9v8-6v38
CVE: CVE-2026-33169
CWE: CWE-1333, CWE-400
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-cg4j-q9v8-6v38
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=8.1.0.beta1 <8.1.2.1
- RubyGems: `activesupport` — affected >=8.0.0.beta1 <8.0.4.1
- RubyGems: `activesupport` — affected >=0 <7.2.3.1

## Details
### Impact
`NumberToDelimitedConverter` used a regular expression with `gsub!` to insert thousands delimiters. This could produce quadratic time complexity on long digit strings.

### Releases
The fixed releases are available at the normal locations.

### Credit
This issue was responsibly reported by Hackerone researcher [scyoon](https://hackerone.com/scyoon).

## References
- https://github.com/rails/rails/security/advisories/GHSA-cg4j-q9v8-6v38
- https://nvd.nist.gov/vuln/detail/CVE-2026-33169
- https://github.com/rails/rails/commit/29154f1097da13d48fdb3200760b3e3da66dcb11
- https://github.com/rails/rails/commit/b54a4b373c6f042cab6ee2033246b1c9ecc38974
- https://github.com/rails/rails/commit/ec1a0e215efd27a3b3911aae6df978a80f456a49
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.2.3.1
- https://github.com/rails/rails/releases/tag/v8.0.4.1
- https://github.com/rails/rails/releases/tag/v8.1.2.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activesupport/CVE-2026-33169.yml
