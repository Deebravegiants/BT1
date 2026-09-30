# [M] openssl-encrypt before 1.4.9 Password Cleartext Leak via Debug

## Summary
Severity: Medium
Advisory: CVE-2026-81705
Aliases: GHSA-jgvm-7jxv-cgcc, PYSEC-2026-3780
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81705
Type: osv

## Details
openssl-encrypt before 1.4.9 fails to redact the file password in its --debug argv dump when the password is supplied via bundled short-option spellings (e.g. -apHunter2) or abbreviated long-option spellings (e.g. --passw). The sanitizer only recognized exact option names, --option=value forms, and tokens starting with -p, so these spellings bypass the redaction chokepoint and the cleartext password is written to stderr. Anyone with access to that output (terminal scrollback, merged 2>&1 output, CI job logs, or the GUI's persistent debug log) can recover the password.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81705.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-jgvm-7jxv-cgcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-81705
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-password-cleartext-leak-via-debug
