# [M] Rails Multisite secure/signed cookies share secrets between sites in a multi-site application

## Summary
Severity: Medium
Advisory: GHSA-844m-cpr9-jcmh
CVE: CVE-2021-41263
CWE: CWE-200, CWE-327, CWE-565
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2021-11-15
Source: https://github.com/advisories/GHSA-844m-cpr9-jcmh
Type: github-advisory

## Affected
- RubyGems: `rails_multisite` — affected >=0 <4.0.0

## Details
### Impact
This vulnerability impacts any Rails applications using `rails_multisite` alongside Rails' signed/encrypted cookies. Depending on how the application makes use of these cookies, it may be possible for an attacker to re-use cookies on different 'sites' within a multi-site Rails application.

### Patches
The issue has been patched in v4 of the `rails_multisite` gem. Note that this upgrade will invalidate all previous signed/encrypted cookies. The impact of this invalidation will vary based on the application architecture.

## References
- https://github.com/discourse/rails_multisite/security/advisories/GHSA-844m-cpr9-jcmh
- https://nvd.nist.gov/vuln/detail/CVE-2021-41263
- https://github.com/discourse/rails_multisite/commit/c6785cdb5c9277dd2c5ac8d55180dd1ece440ed0
- https://github.com/discourse/rails_multisite
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails_multisite/CVE-2021-41263.yml
