# [H] CryptoLib command Injection vulnerability in initialize_kerberos_keytab_file_login()

## Summary
Severity: High
Advisory: CVE-2025-59534
Aliases: GHSA-jw5c-58hr-m3v3
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-59534
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. Prior to version 1.4.2, there is a command Injection vulnerability in initialize_kerberos_keytab_file_login(). The vulnerability exists because the code directly interpolates user-controlled input into a shell command and executes it via system() without any sanitization or validation. This issue has been patched in version 1.4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59534.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-jw5c-58hr-m3v3
- https://nvd.nist.gov/vuln/detail/CVE-2025-59534
- https://github.com/nasa/CryptoLib/commit/3ccb1b306026bb20a028fbfdcf18935f7345ed2f
