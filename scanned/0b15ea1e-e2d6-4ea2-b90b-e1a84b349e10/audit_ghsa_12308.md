# [H] crack does not properly restrict casts of string values

## Summary
Severity: High
Advisory: GHSA-m7fq-cf8q-35q7
CVE: CVE-2013-1800
CWE: CWE-704, CWE-74
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-m7fq-cf8q-35q7
Type: github-advisory

## Affected
- RubyGems: `crack` — affected >=0 <0.3.2

## Details
The crack gem 0.3.1 and earlier for Ruby does not properly restrict casts of string values, which might allow remote attackers to conduct object-injection attacks and execute arbitrary code, or cause a denial of service (memory and CPU consumption) by leveraging Action Pack support for (1) YAML type conversion or (2) Symbol type conversion, a similar vulnerability to CVE-2013-0156.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1800
- https://github.com/jnunemaker/crack/commit/e3da1212a1f84a898ee3601336d1dbbf118fb5f6
- https://bugzilla.novell.com/show_bug.cgi?id=804721
- https://bugzilla.redhat.com/show_bug.cgi?id=917236
- https://github.com/jnunemaker/crack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/crack/CVE-2013-1800.yml
- https://support.cloud.engineyard.com/entries/22915701-january-14-2013-security-vulnerabilities-httparty-extlib-crack-nori-update-these-gems-immediately
- https://web.archive.org/web/20130203232028/https://support.cloud.engineyard.com/entries/22915701-january-14-2013-security-vulnerabilities-httparty-extlib-crack-nori-update-these-gems-immediately
- http://lists.opensuse.org/opensuse-security-announce/2013-04/msg00003.html
