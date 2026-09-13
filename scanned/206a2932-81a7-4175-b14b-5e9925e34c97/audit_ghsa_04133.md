# [M] devise Time-of-check Time-of-use Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-73rf-6mrf-759q
CVE: CVE-2019-5421
CWE: CWE-367
Ecosystem: RubyGems
Published: 2019-03-19
Source: https://github.com/advisories/GHSA-73rf-6mrf-759q
Type: github-advisory

## Affected
- RubyGems: `devise` — affected >=0 <4.6.0

## Details
Devise ruby gem before 4.6.0 when the `lockable` module is used is vulnerable to a time-of-check time-of-use (TOCTOU) race condition due to `increment_failed_attempts` within the `Devise::Models::Lockable` class not being concurrency safe.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5421
- https://github.com/plataformatec/devise/issues/4981
- https://github.com/plataformatec/devise/pull/4996
- https://github.com/plataformatec/devise
