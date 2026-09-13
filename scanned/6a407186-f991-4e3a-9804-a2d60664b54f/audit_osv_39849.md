# [M] ZipTransformer uses file_name header to build workDirectory path without sanitization

## Summary
Severity: Medium
Advisory: CVE-2026-47862
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47862
Type: osv

## Details
An attacker who can set the file_name header on a message reaching a ZipTransformer with ZipResultType.FILE (the default) can cause the resulting .zip archive to be written to an arbitrary filesystem path outside the configured workDirectory.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12

## References
- https://spring.io/security/cve-2026-47862
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47862.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47862
