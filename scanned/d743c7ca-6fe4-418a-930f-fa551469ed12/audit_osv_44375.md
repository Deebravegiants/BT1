# [M] openssl_encrypt before 1.4.9 Credential Exposure via Debug Output

## Summary
Severity: Medium
Advisory: CVE-2026-81715
Aliases: GHSA-jqqp-pf9j-889j, PYSEC-2026-3964
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81715
Type: osv

## Details
openssl_encrypt (pip package openssl-encrypt) versions <= 1.4.8 do not redact the keyserver bearer token passed as the positional argument to 'keyserver set-token' in the --debug argv dump, because sanitize_argv_for_debug fails to sanitize it. As a result the token is printed in cleartext to stderr under --debug (even without --unsafe-show-secrets), persisting the credential in logs and terminal history. Fixed in 1.4.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81715.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-jqqp-pf9j-889j
- https://nvd.nist.gov/vuln/detail/CVE-2026-81715
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-credential-exposure-via-debug-output
