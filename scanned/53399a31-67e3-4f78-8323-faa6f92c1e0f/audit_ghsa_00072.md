# [H] Ruby-ffi has a DLL loading issue 

## Summary
Severity: High
Advisory: GHSA-2gw2-8q9w-cw8p
CVE: CVE-2018-1000201
CWE: CWE-426
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-31
Source: https://github.com/advisories/GHSA-2gw2-8q9w-cw8p
Type: github-advisory

## Affected
- RubyGems: `ffi` — affected >=0 <1.9.24

## Details
ruby-ffi version 1.9.23 and earlier has a DLL loading issue which can be hijacked on Windows OS, when a Symbol is used as DLL name instead of a String This vulnerability appears to have been fixed in v1.9.24 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000201
- https://github.com/ffi/ffi/commit/09e0c6076466b4383da7fa4e13f714311109945a
- https://github.com/ffi/ffi/commit/e0fe486df0e117ed67b0282b6ada04b7214ca05c
- https://github.com/ffi/ffi
- https://github.com/ffi/ffi/releases/tag/1.9.24
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ffi/CVE-2018-1000201.yml
