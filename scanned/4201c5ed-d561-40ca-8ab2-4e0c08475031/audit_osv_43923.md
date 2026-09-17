# [M] Memory-amplification denial of service via GZIP decompression bomb in Amazon ion-java

## Summary
Severity: Medium
Advisory: CVE-2026-75936
Aliases: GHSA-wj53-jv76-65mc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75936
Type: osv

## Details
Improper handling of highly compressed data in the GZIP auto-decompression handler in Amazon ion-java before 1.12.0 might allow remote actors to cause a denial of service via a crafted compressed Ion document that expands to an arbitrarily large size upon decompression.



To remediate this issue, users should upgrade to version 1.12.0 and configure withGzipDecompressionEnabled(false) and/or set an explicit withMaximumBufferSize() when parsing untrusted input.

## References
- https://aws.amazon.com/security/security-bulletins/2026-083-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75936.json
- https://github.com/amazon-ion/ion-java/security/advisories/GHSA-wj53-jv76-65mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-75936
- https://github.com/amazon-ion/ion-java/releases/tag/v1.12.0
