# [M] private_address_check vulnerable to bypass of Resolv.getaddresses method

## Summary
Severity: Medium
Advisory: GHSA-hxhj-hp9m-qwc4
CVE: CVE-2017-0904
CWE: CWE-242
Ecosystem: RubyGems
Published: 2017-11-29
Source: https://github.com/advisories/GHSA-hxhj-hp9m-qwc4
Type: github-advisory

## Affected
- RubyGems: `private_address_check` — affected >=0 <0.4.0

## Details
The private_address_check ruby gem before 0.4.0 is vulnerable to a bypass due to use of Ruby's `Resolv.getaddresses` method, which is OS-dependent and should not be relied upon for security measures, such as when used to blacklist private network addresses to prevent server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0904
- https://github.com/jtdowney/private_address_check/issues/1
- https://github.com/jtdowney/private_address_check/commit/58a0d7fe31de339c0117160567a5b33ad82b46af
- https://hackerone.com/reports/287245
- https://hackerone.com/reports/287835
- https://edoverflow.com/2017/ruby-resolv-bug
