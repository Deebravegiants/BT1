# [M] Excon does not redact additional sensitive/risky headers when following redirects

## Summary
Severity: Medium
Advisory: GHSA-48rx-c7pg-q66r
CVE: CVE-2026-54171
CWE: CWE-200, CWE-201, CWE-522
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-48rx-c7pg-q66r
Type: github-advisory

## Affected
- RubyGems: `excon` — affected >=0 <1.5.0

## Details
### Impact
The redirect follower middleware previously failed to strip a number of headers that are known to be sensitive and did not provide a way to provide a custom list of headers to strip. 

_What kind of vulnerability is it? Who is impacted?_
This could cause inadvertent leakage of sensitive data for users of the RedirectFollower middleware in cases where the initial request includes header information that is not intended for the new target.

### Patches
Patch exists and is released in v1.5.0

### Workarounds
Users can backport the [fix](https://github.com/excon/excon/commit/ea89a35308a12f4b791b6c50f2cbd33f94889fa3) to a custom redirect follower middleware.

## References
- https://github.com/excon/excon/security/advisories/GHSA-48rx-c7pg-q66r
- https://nvd.nist.gov/vuln/detail/CVE-2026-54171
- https://github.com/excon/excon/pull/901
- https://github.com/excon/excon/commit/ea89a35308a12f4b791b6c50f2cbd33f94889fa3
- https://github.com/excon/excon
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/excon/CVE-2026-54171.yml
- https://www.cve.org/CVERecord?id=CVE-2026-54171
