# [H] phpseclib's AES-CBC unpadding susceptible to padding oracle timing attack

## Summary
Severity: High
Advisory: GHSA-94g3-g5v7-q4jg
CVE: CVE-2026-32935
CWE: CWE-208
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-94g3-g5v7-q4jg
Type: github-advisory

## Affected
- Packagist: `phpseclib/phpseclib` — affected >=3.0.0 <3.0.50
- Packagist: `phpseclib/phpseclib` — affected >=2.0.0 <2.0.52
- Packagist: `phpseclib/phpseclib` — affected >=0.1.1 <1.0.27

## Details
### Impact
Those using AES in CBC mode may be susceptible to a padding oracle timing attack.

### Patches
https://github.com/phpseclib/phpseclib/commit/ccc21aef71eb170e9bf819b167e67d1fd9e6e788

### Workarounds
Use AES in CTR, CFB or OFB modes

### References
https://github.com/phpseclib/phpseclib/commit/ccc21aef71eb170e9bf819b167e67d1fd9e6e788

## References
- https://github.com/phpseclib/phpseclib/security/advisories/GHSA-94g3-g5v7-q4jg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32935
- https://github.com/phpseclib/phpseclib/commit/ccc21aef71eb170e9bf819b167e67d1fd9e6e788
- https://github.com/phpseclib/phpseclib
