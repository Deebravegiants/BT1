# [M] Unbounded decompression in UnZipTransformer enables zip-bomb DoS

## Summary
Severity: Medium
Advisory: CVE-2026-59274
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59274
Type: osv

## Details
The UnZipTransformer does not limit decompressed entry size or entry count when processing archives. Consequently, an attacker can send a zip archive that can exhaust JVM heap memory, causing a denial-of-service outage.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12

## References
- https://spring.io/security/cve-2026-59274
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59274.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59274
