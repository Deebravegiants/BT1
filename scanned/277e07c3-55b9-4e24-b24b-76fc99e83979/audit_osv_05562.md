# [H] BIT-golang-2020-0601

## Summary
Severity: High
Advisory: BIT-golang-2020-0601
Aliases: CVE-2020-0601, GO-2022-0535
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2020-0601
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.13.0 <1.13.7

## Details
A spoofing vulnerability exists in the way Windows CryptoAPI (Crypt32.dll) validates Elliptic Curve Cryptography (ECC) certificates.An attacker could exploit the vulnerability by using a spoofed code-signing certificate to sign a malicious executable, making it appear the file was from a trusted, legitimate source, aka 'Windows CryptoAPI Spoofing Vulnerability'.

## References
- http://packetstormsecurity.com/files/155960/CurveBall-Microsoft-Windows-CryptoAPI-Spoofing-Proof-Of-Concept.html
- http://packetstormsecurity.com/files/155961/CurveBall-Microsoft-Windows-CryptoAPI-Spoofing-Proof-Of-Concept.html
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0601
- https://nvd.nist.gov/vuln/detail/CVE-2020-0601
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-0601
