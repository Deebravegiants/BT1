# [M] openssl_encrypt before 1.4.9 Denial of Service via QR total field

## Summary
Severity: Medium
Advisory: CVE-2026-81693
Aliases: GHSA-r23m-gf2m-8www, PYSEC-2026-3798
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81693
Type: osv

## Details
openssl_encrypt before 1.4.9 fails to validate the total field from QR JSON payloads before materializing ranges. Attackers can supply crafted QR images with extremely large total values to trigger unbounded memory allocation and cause denial of service through out-of-memory conditions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81693.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-r23m-gf2m-8www
- https://nvd.nist.gov/vuln/detail/CVE-2026-81693
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-denial-of-service-via-qr-total-field
