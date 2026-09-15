# [H] Ruby JSON has a format string injection vulnerability

## Summary
Severity: High
Advisory: GHSA-3m6g-2423-7cp3
CVE: CVE-2026-33210
CWE: CWE-134
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-3m6g-2423-7cp3
Type: github-advisory

## Affected
- RubyGems: `json` — affected >=2.18.0 <2.19.2
- RubyGems: `json` — affected >=2.16.0 <2.17.1.2
- RubyGems: `json` — affected >=2.14.0 <2.15.2.1

## Details
### Impact

A format string injection vulnerability than that lead to denial of service attacks or information disclosure, when the `allow_duplicate_key: false` parsing option is used to parse user supplied documents. 

This option isn't the default, if you didn't opt-in to use it, you are not impacted.

### Patches

Patched in `2.19.2`.

### Workarounds

The issue can be avoided by not using the `allow_duplicate_key: false` parsing option.

## References
- https://github.com/ruby/json/security/advisories/GHSA-3m6g-2423-7cp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33210
- https://github.com/ruby/json
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/json/CVE-2026-33210.yml
