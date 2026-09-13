# [H] Ruby-saml allows attackers to perform XML signature wrapping attacks 

## Summary
Severity: High
Advisory: GHSA-36p7-xjw8-h6f2
CVE: CVE-2016-5697
CWE: CWE-91
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-08-21
Source: https://github.com/advisories/GHSA-36p7-xjw8-h6f2
Type: github-advisory

## Affected
- RubyGems: `ruby-saml` — affected >=0 <1.3.0

## Details
ruby-saml prior to version 1.3.0 is vulnerable to an XML signature wrapping attack in the specific scenario where there was a signature that referenced at the same time 2 elements (but past the scheme validator process since 1 of the element was inside the encrypted assertion).
ruby-saml users must update to 1.3.0, which implements 3 extra validations to mitigate this kind of attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5697
- https://github.com/onelogin/ruby-saml/commit/a571f52171e6bfd87db59822d1d9e8c38fb3b995
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-saml/CVE-2016-5697.yml
- http://www.openwall.com/lists/oss-security/2016/06/24/3
