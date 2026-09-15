# [H] Out-of-bounds Read in Ruby JSON Parser 

## Summary
Severity: High
Advisory: GHSA-9m3q-rhmv-5q44
CVE: CVE-2025-27788
CWE: CWE-125
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-9m3q-rhmv-5q44
Type: github-advisory

## Affected
- RubyGems: `json` — affected >=2.10.0 <2.10.2

## Details
### Impact

A specially crafted document could cause an out of bound read, most likely resulting in a crash.

Versions 2.10.0 and 2.10.1 are impacted. Older versions are not.

### Patches

Version 2.10.2 fixes the problem.

### Workarounds

None.

## References
- https://github.com/ruby/json/security/advisories/GHSA-9m3q-rhmv-5q44
- https://nvd.nist.gov/vuln/detail/CVE-2025-27788
- https://github.com/ruby/json/commit/c56db31f800d5d508389793e69682f99749dbadf
- https://github.com/ruby/json
- https://github.com/ruby/json/releases/tag/v2.10.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/json/CVE-2025-27788.yml
