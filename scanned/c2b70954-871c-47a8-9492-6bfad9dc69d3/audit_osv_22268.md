# [H] Improper Input Validation leading to Path Traversal in CycloneDX BOM Repository Server

## Summary
Severity: High
Advisory: CVE-2022-24774
Aliases: GHSA-6c74-9588-wq9j
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2022-03-22
Source: https://osv.dev/vulnerability/CVE-2022-24774
Type: osv

## Details
CycloneDX BOM Repository Server is a bill of materials (BOM) repository server for distributing CycloneDX BOMs. CycloneDX BOM Repository Server before version 2.0.1 has an improper input validation vulnerability leading to path traversal. A malicious user may potentially exploit this vulnerability to create arbitrary directories or a denial of service by deleting arbitrary directories. The vulnerability is resolved in version 2.0.1. The vulnerability is not exploitable with the default configuration with the post and delete methods disabled. This can be configured by modifying the `appsettings.json` file, or alternatively, setting the environment variables `ALLOWEDMETHODS__POST` and `ALLOWEDMETHODS__DELETE` to `false`.

## References
- https://github.com/CycloneDX/cyclonedx-bom-repo-server/releases/tag/v2.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24774.json
- https://github.com/CycloneDX/cyclonedx-bom-repo-server/security/advisories/GHSA-6c74-9588-wq9j
- https://nvd.nist.gov/vuln/detail/CVE-2022-24774
- https://github.com/CycloneDX/cyclonedx-bom-repo-server/commit/001a3278b5572e52c0ecac0bd1157bf2599502b7
