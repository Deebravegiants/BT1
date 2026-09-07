# [M] rack-mini-profiler allows remote attackers to obtain sensitive information about allocated strings and objects

## Summary
Severity: Medium
Advisory: GHSA-j5hj-fhc9-g24m
CVE: CVE-2016-4442
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-j5hj-fhc9-g24m
Type: github-advisory

## Affected
- RubyGems: `rack-mini-profiler` — affected >=0 <0.10.1

## Details
The rack-mini-profiler gem before 0.10.1 for Ruby allows remote attackers to obtain sensitive information about allocated strings and objects by leveraging incorrect ordering of security checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4442
- https://github.com/MiniProfiler/rack-mini-profiler/commit/4273771d65f1a7411e3ef5843329308d0e2d257c
- https://github.com/MiniProfiler/rack-mini-profiler
- https://github.com/MiniProfiler/rack-mini-profiler/blob/v0.10.1/CHANGELOG.md
- http://www.openwall.com/lists/oss-security/2016/06/10/2
