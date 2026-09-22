# [H] Ox gem crashes due to a crafted input

## Summary
Severity: High
Advisory: GHSA-pjj4-w39g-pw54
CVE: CVE-2017-15928
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-11-21
Source: https://github.com/advisories/GHSA-pjj4-w39g-pw54
Type: github-advisory

## Affected
- RubyGems: `ox` — affected >=0 <2.8.1

## Details
In the Ox gem 2.8.0 for Ruby, the process crashes with a segmentation fault when a crafted input is supplied to `parse_obj`. NOTE: the vendor has stated "Ox should handle the error more gracefully" but has not confirmed a security implication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15928
- https://github.com/ohler55/ox/issues/194
- https://github.com/ohler55/ox
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ox/CVE-2017-15928.yml
- https://rubygems.org/gems/ox/versions/2.8.0
