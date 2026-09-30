# [H] HTTParty does not restrict casts of string values

## Summary
Severity: High
Advisory: GHSA-mgx3-27hr-mfgp
CVE: CVE-2013-1801
CWE: CWE-74
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-mgx3-27hr-mfgp
Type: github-advisory

## Affected
- RubyGems: `httparty` — affected >=0 <0.10.0

## Details
The httparty gem 0.9.0 and earlier for Ruby does not properly restrict casts of string values, which might allow remote attackers to conduct object-injection attacks and execute arbitrary code, or cause a denial of service (memory and CPU consumption) by leveraging Action Pack support for YAML type conversion, a similar vulnerability to CVE-2013-0156.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1801
- https://github.com/jnunemaker/httparty/commit/53a812426dd32108d6cba4272b493aa03bc8c031
- https://bugzilla.redhat.com/show_bug.cgi?id=917229
- https://github.com/jnunemaker/httparty
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/httparty/CVE-2013-1801.yml
- https://support.cloud.engineyard.com/entries/22915701-january-14-2013-security-vulnerabilities-httparty-extlib-crack-nori-update-these-gems-immediately
- https://web.archive.org/web/20200229101716/http://www.securityfocus.com/bid/58260
