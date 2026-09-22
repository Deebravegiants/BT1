# [H] react-native-keys insecurely stores encryption cipher and Base64 chunks

## Summary
Severity: High
Advisory: GHSA-fj44-h6xw-896g
CVE: CVE-2025-45001
CWE: CWE-312
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-fj44-h6xw-896g
Type: github-advisory

## Affected
- npm: `react-native-keys` — affected >=0

## Details
react-native-keys 0.7.11 is vulnerable to sensitive information disclosure (remote) as encryption cipher and Base64 chunks are stored as plaintext in the compiled native binary. Attackers can extract these secrets using basic static analysis tools.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-45001
- https://gist.github.com/ch3tanbug/44aedff79dd5d2d6beadbffcd01e0de5
- https://github.com/ch3tanbug/vulnerability-research/tree/main/CVE-2025-45001
- https://github.com/numandev1/react-native-keys
