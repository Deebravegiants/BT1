# [M] Schule Has Insecure OTP Length, is Susceptible to Brute-Force Attacks

## Summary
Severity: Medium
Advisory: CVE-2025-48372
Aliases: GHSA-6c48-67xx-vqgc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-48372
Type: osv

## Details
Schule is open-source school management system software. The generateOTP() function generates a 4-digit numeric One-Time Password (OTP). Prior to version 1.0.1, even if a secure random number generator is used, the short length and limited range (1000–9999) results in only 9000 possible combinations. This small keyspace makes the OTP highly vulnerable to brute-force attacks, especially in the absence of strong rate-limiting or lockout mechanisms. Version 1.0.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48372.json
- https://github.com/schule111/Schule/security/advisories/GHSA-6c48-67xx-vqgc
- https://nvd.nist.gov/vuln/detail/CVE-2025-48372
- https://github.com/schule111/Schule/commit/cd53abbea93943f2c60a5281d45bebadc57636b7
