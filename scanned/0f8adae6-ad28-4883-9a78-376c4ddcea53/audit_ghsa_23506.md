# [H] Hex authenticity of signed packages not validated

## Summary
Severity: High
Advisory: GHSA-q3cc-rr2c-87r6
CVE: CVE-2019-1000013
CWE: CWE-345
Ecosystem: Hex
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q3cc-rr2c-87r6
Type: github-advisory

## Affected
- Hex: `hex_core` — affected >=0 <0.4.0

## Details
Hex package manager hex_core version 0.3.0 and earlier contains a Signing oracle vulnerability in Package registry verification that can result in Package modifications not detected, allowing code execution. This attack appears to be exploitable via victim fetches packages from malicious/compromised mirror. This vulnerability appears to have been fixed in 0.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1000013
- https://github.com/hexpm/hex_core/pull/48
- https://github.com/hexpm/hex_core/pull/51
- https://github.com/hexpm/hex_core
