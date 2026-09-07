# [M] Clockwork Web contains a Cross-Site Request Forgery Vulnerability with Rails < 5.2

## Summary
Severity: Medium
Advisory: GHSA-p4xx-w6fr-c4w9
CVE: CVE-2023-25015
CWE: CWE-352, CWE-652
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-02-02
Source: https://github.com/advisories/GHSA-p4xx-w6fr-c4w9
Type: github-advisory

## Affected
- RubyGems: `clockwork_web` — affected >=0 <0.1.2

## Details
Clockwork Web before 0.1.2, when used with Rails before 5.2 is used, allows Cross-Site Request Forgery (CSRF). A CSRF attack works by getting an authorized user to visit a malicious website and then performing requests on behalf of the user. In this instance, actions include enabling and disabling jobs. All users running an affected release on Rails < 5.2 should upgrade immediately.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25015
- https://github.com/ankane/clockwork_web/issues/4
- https://github.com/ankane/clockwork_web/commit/ec2896503ee231588547c2fad4cb93a94e78f857
- https://github.com/ankane/clockwork_web
- https://github.com/ankane/clockwork_web/compare/v0.1.1...v0.1.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/clockwork_web/CVE-2023-25015.yml
