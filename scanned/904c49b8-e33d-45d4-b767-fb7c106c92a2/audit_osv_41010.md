# [H] Adminer before 5.4.3 CSRF Token Secret Recovery via XOR Masking

## Summary
Severity: High
Advisory: CVE-2026-56706
Aliases: GHSA-33j4-hc95-pggg
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-56706
Type: osv

## Details
Adminer before 5.4.3 uses a CSRF token scheme that transmits both the XOR mask and the masked value in every token (format (rand XOR secret):rand), allowing anyone who observes a single CSRF token (e.g., via network sniffing, log files, Referrer header, or XSS) to recover the session secret with a single XOR operation and forge unlimited valid tokens. The implementation is further weakened by a low-entropy session token (rand(1,1e6), ~20 bits) that permits blind brute-force, and by use of loose comparison (==) in token verification, enabling PHP type juggling. Exploitation enables cross-site request forgery against authenticated sessions, including execution of arbitrary SQL queries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56706.json
- https://github.com/vrana/adminer/security/advisories/GHSA-33j4-hc95-pggg
- https://nvd.nist.gov/vuln/detail/CVE-2026-56706
- https://www.vulncheck.com/advisories/adminer-before-csrf-token-secret-recovery-via-xor-masking
