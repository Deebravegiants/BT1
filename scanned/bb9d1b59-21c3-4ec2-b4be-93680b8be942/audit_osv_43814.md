# [C] openssl_encrypt before 1.4.0 Logging Bug and Race Condition

## Summary
Severity: Critical
Advisory: CVE-2026-74885
Aliases: GHSA-43r4-3hf9-m84q, PYSEC-2026-3762
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74885
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain a logging bug in restore_hidden_modules() that logs module counts after clearing, always showing zero restored modules and corrupting audit trails. Additionally, a race condition exists between module hiding and import hook installation where another thread could re-import blocked modules in multi-threaded environments.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74885.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-43r4-3hf9-m84q
- https://nvd.nist.gov/vuln/detail/CVE-2026-74885
- https://www.vulncheck.com/advisories/openssl-encrypt-before-logging-bug-and-race-condition
