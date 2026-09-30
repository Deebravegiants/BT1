# [M] Altcha Proof-of-Work obfuscation mode cryptanalytic break

## Summary
Severity: Medium
Advisory: GHSA-mpmc-qchh-r9q8
CVE: CVE-2025-65849
CWE: CWE-327
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-mpmc-qchh-r9q8
Type: github-advisory

## Affected
- npm: `altcha` — affected >=0.8.0

## Details
A cryptanalytic break in Altcha Proof-of-Work obfuscation mode version 0.8.0 and later allows for remote visitors to recover the Proof-of-Work nonce in constant time via mathematical deduction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65849
- https://altcha.org/docs/v2/obfuscation
- https://github.com/altcha-org/altcha
- https://github.com/altcha-org/altcha/blob/154f874cbcdd4e639783463130d13988a2bd1bdc/src/helpers.ts#L170-L194
- https://github.com/eternal-flame-AD/altcha-deobfs
