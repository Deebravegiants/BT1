# [M] openssl_encrypt before 1.4.9 Denial of Service via Unbounded Argon2

## Summary
Severity: Medium
Advisory: CVE-2026-81720
Aliases: GHSA-783h-8q2f-f762, PYSEC-2026-3965
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81720
Type: osv

## Details
openssl_encrypt before 1.4.9 fails to validate the memory_cost parameter from identity file protection blocks, allowing attackers to trigger out-of-memory conditions during key derivation. Attackers with write access to local identity stores can craft malicious identity files with excessive memory_cost values that cause the host to crash when unlocking identities before authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81720.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-783h-8q2f-f762
- https://nvd.nist.gov/vuln/detail/CVE-2026-81720
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-denial-of-service-via-unbounded-argon2
