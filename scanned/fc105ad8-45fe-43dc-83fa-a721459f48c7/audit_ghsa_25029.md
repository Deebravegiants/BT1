# [M] Spree does not properly restrict the use of a hash to provide values for a model's attributes

## Summary
Severity: Medium
Advisory: GHSA-7h48-m3rw-vr27
CVE: CVE-2008-7310
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7h48-m3rw-vr27
Type: github-advisory

## Affected
- RubyGems: `spree` — affected >=0 <0.4.0

## Details
Spree 0.2.0 does not properly restrict the use of a hash to provide values for a model's attributes, which allows remote attackers to set the Order state value and bypass the intended payment step via a modified URL, related to a "mass assignment" vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-7310
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree/CVE-2008-7310.yml
- https://github.com/spree/spree
- https://spreecommerce.com/blog/security-vulnerability-mass-assignment
- https://web.archive.org/web/20080925003904/http://railspikes.com/2008/9/22/is-your-rails-application-safe-from-mass-assignment
- https://web.archive.org/web/20101128024717/http://spreecommerce.com/blog/2008/09/16/security-vulnerability-mass-assignment-of-order-params
- http://railspikes.com/2008/9/22/is-your-rails-application-safe-from-mass-assignment
- http://spreecommerce.com/blog/2008/09/16/security-vulnerability-mass-assignment-of-order-params
