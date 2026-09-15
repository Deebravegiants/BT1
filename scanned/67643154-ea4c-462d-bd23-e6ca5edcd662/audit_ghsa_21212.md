# [C] otp-generator before v3.0.0 insecurely generates random one-time passwords

## Summary
Severity: Critical
Advisory: GHSA-6x93-h9g3-9phr
CVE: CVE-2021-23451
CWE: CWE-330
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-6x93-h9g3-9phr
Type: github-advisory

## Affected
- npm: `otp-generator` — affected >=0 <3.0.0

## Details
The package otp-generator before 3.0.0 are vulnerable to Insecure Randomness due to insecure generation of random one-time passwords, which may allow a brute-force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23451
- https://github.com/Maheshkumar-Kakade/otp-generator/issues/12
- https://github.com/Maheshkumar-Kakade/otp-generator/commit/b27de1ce439ae7f533cec26677e9698671275b70
- https://github.com/Maheshkumar-Kakade/otp-generator
- https://security.snyk.io/vuln/SNYK-JS-OTPGENERATOR-1655480
