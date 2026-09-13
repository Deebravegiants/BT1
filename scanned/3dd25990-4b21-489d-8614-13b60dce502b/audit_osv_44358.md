# [M] openssl_encrypt before 1.4.9 Credential Leakage via Unvalidated Server URLs

## Summary
Severity: Medium
Advisory: CVE-2026-81691
Aliases: GHSA-xr64-hcxg-4ghr, PYSEC-2026-3797
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81691
Type: osv

## Details
openssl_encrypt versions before 1.4.9 fail to validate server URLs in login and register_with_email functions, accepting unencrypted http:// URLs and unconfigured hosts. Attackers on the network path can intercept cleartext credentials including client_id, passwords, and JWTs to achieve full keyserver account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81691.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-xr64-hcxg-4ghr
- https://nvd.nist.gov/vuln/detail/CVE-2026-81691
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-credential-leakage-via-unvalidated-server-urls
