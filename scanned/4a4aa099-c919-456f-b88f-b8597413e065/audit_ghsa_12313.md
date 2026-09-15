# [H] extlib does not properly restrict casts of string values

## Summary
Severity: High
Advisory: GHSA-9h36-4jf2-hx53
CVE: CVE-2013-1802
CWE: CWE-704
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-9h36-4jf2-hx53
Type: github-advisory

## Affected
- RubyGems: `extlib` — affected >=0 <0.9.16

## Details
The extlib gem 0.9.15 and earlier for Ruby does not properly restrict casts of string values, which might allow remote attackers to conduct object-injection attacks and execute arbitrary code, or cause a denial of service (memory and CPU consumption) by leveraging Action Pack support for (1) YAML type conversion or (2) Symbol type conversion, a similar vulnerability to CVE-2013-0156.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1802
- https://bugzilla.redhat.com/show_bug.cgi?id=917233
- https://github.com/datamapper/extlib
- https://github.com/datamapper/extlib/compare/b4f98174ec35ac96f76a08d5624fad05d22879b5...4540e7102b803624cc2eade4bb8aaaa934fc31c5
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/extlib/CVE-2013-1802.yml
- https://web.archive.org/web/20130203232028/https://support.cloud.engineyard.com/entries/22915701-january-14-2013-security-vulnerabilities-httparty-extlib-crack-nori-update-these-gems-immediately
- http://lists.opensuse.org/opensuse-security-announce/2013-04/msg00002.html
