# [C] Froxlor guessable password reset token

## Summary
Severity: Critical
Advisory: GHSA-qj6h-m7xc-r2v3
CVE: CVE-2016-5100
CWE: CWE-330
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qj6h-m7xc-r2v3
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <0.9.35

## Details
Froxlor before 0.9.35 uses the PHP rand function for random number generation, which makes it easier for remote attackers to guess the password reset token by predicting a value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5100
- https://github.com/Froxlor/Froxlor/commit/da4ec3e1b591de96675817a009e26e05e848a6ba
- https://github.com/Froxlor/Froxlor
