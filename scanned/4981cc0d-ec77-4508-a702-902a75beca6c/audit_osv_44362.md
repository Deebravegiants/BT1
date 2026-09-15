# [C] openssl_encrypt before 1.4.9 Terminal Injection via key_id

## Summary
Severity: Critical
Advisory: CVE-2026-81695
Aliases: GHSA-jwfm-99h7-2w5x, PYSEC-2026-3774
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81695
Type: osv

## Details
openssl_encrypt versions before 1.4.9 fail to escape attacker-controlled key_id values printed to stderr during decrypt auto-detection. Attackers can craft encrypted files with malicious key_id containing escape sequences to repaint terminal output and forge authenticity verification blocks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81695.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-jwfm-99h7-2w5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-81695
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-terminal-injection-via-key-id
