# [M] openssl_encrypt before 1.4.0 Hardcoded Secret Key

## Summary
Severity: Medium
Advisory: CVE-2026-74892
Aliases: GHSA-p926-6hjp-w9jw, PYSEC-2026-3746
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74892
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain a hardcoded default secret key in the standalone telemetry server configuration that is used for API key hashing. Attackers who know this default value can predict or forge API key hashes to compromise telemetry API authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74892.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-p926-6hjp-w9jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-74892
- https://www.vulncheck.com/advisories/openssl-encrypt-before-hardcoded-secret-key
