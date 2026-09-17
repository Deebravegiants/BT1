# [M] Arbitrary File Write via Path Traversal in ResourceCacheService

## Summary
Severity: Medium
Advisory: CVE-2026-59294
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59294
Type: osv

## Details
ResourceCacheService.getCacheName() builds the on-disk filename by appending the URI fragment verbatim, without stripping path separators or .. sequences, and passes the result to new File(resourceParentFolder, newFileName) before writing the downloaded bytes there.
Spring AI 2.0.0
Spring AI 1.1.0 - 1.1.8
Spring AI 1.0.9 and earlier

## References
- https://spring.io/security/cve-2026-59294
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59294.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59294
