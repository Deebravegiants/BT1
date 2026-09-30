# [M] Features file injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-42gq-h7xj-33r4
CVE: CVE-2013-4318
CWE: CWE-74
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-42gq-h7xj-33r4
Type: github-advisory

## Affected
- RubyGems: `features` — affected >=0

## Details
File injection vulnerability in Ruby gem Features 0.3.0 allows remote attackers to inject malicious html in the `/tmp` directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4318
- https://github.com/mhennemeyer/features
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/features/CVE-2013-4318.yml
- https://security-tracker.debian.org/tracker/CVE-2013-4318
- http://www.openwall.com/lists/oss-security/2013/09/09/10
