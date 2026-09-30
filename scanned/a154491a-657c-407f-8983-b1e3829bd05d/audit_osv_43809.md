# [M] openssl_encrypt before 1.4.8 Hardware Pepper Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-74870
Aliases: GHSA-p9g8-wvh4-2jmx, PYSEC-2026-3956
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74870
Type: osv

## Details
openssl_encrypt (pip) versions <= 1.4.7 contain an information exposure vulnerability where the 'hsm fido2-test' and 'hsm onlykey-test' diagnostic commands unconditionally print the full derived hardware pepper as hex to stdout/stderr (crypt_cli.py, handle_hsm_command). The printed value can persist in terminal scrollback, session recordings, or CI logs. Impact is limited because the pepper is derived from a random per-invocation test salt and is salt-bound, so the leaked value cannot be used to decrypt real files. A related plugin issue logged raw prf_data outside the secret-redaction path. Fixed in 1.4.8 (and 1.5.0) by removing the hex dumps and routing plugin debug output through the redaction layer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74870.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-p9g8-wvh4-2jmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-74870
- https://www.vulncheck.com/advisories/openssl-encrypt-before-hardware-pepper-information-disclosure
