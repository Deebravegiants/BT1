# [H] Cross-Site Request Forgery (CSRF) in trestle-auth

## Summary
Severity: High
Advisory: GHSA-h8hx-2c5r-32cf
CVE: CVE-2021-29435
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-h8hx-2c5r-32cf
Type: github-advisory

## Affected
- RubyGems: `trestle-auth` — affected >=0.4.0 <0.4.2

## Details
### Impact
A vulnerability in trestle-auth versions 0.4.0 and 0.4.1 allows an attacker to create a form that will bypass Rails' built-in CSRF protection when submitted by a victim with a trestle-auth admin session. This potentially allows an attacker to alter protected data, including admin account credentials.

### Patches
The vulnerability has been fixed in trestle-auth 0.4.2 released to RubyGems.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [trestle-auth](https://github.com/TrestleAdmin/trestle-auth/issues)
* Email the maintainer at [sam@sampohlenz.com](mailto:sam@sampohlenz.com)

## References
- https://github.com/TrestleAdmin/trestle-auth/security/advisories/GHSA-h8hx-2c5r-32cf
- https://nvd.nist.gov/vuln/detail/CVE-2021-29435
- https://github.com/TrestleAdmin/trestle-auth/commit/cb95b05cdb2609052207af07b4b8dfe3a23c11dc
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/trestle-auth/CVE-2021-29435.yml
- https://rubygems.org/gems/trestle-auth
