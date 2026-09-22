# [C] openssl_encrypt before 1.4.0 JWT Token Forgery via Hardcoded Secrets

## Summary
Severity: Critical
Advisory: CVE-2026-74893
Aliases: GHSA-qc6h-gfjh-7qqg, PYSEC-2026-3768
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74893
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain hardcoded default JWT signing secrets in config.py that pass validation checks. Attackers with access to source code can forge valid JWT tokens for any client_id to gain authenticated access to keyserver and telemetry APIs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74893.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-qc6h-gfjh-7qqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-74893
- https://www.vulncheck.com/advisories/openssl-encrypt-before-jwt-token-forgery-via-hardcoded-secrets
