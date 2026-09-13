# [M] Possible Data Tampering & Loss of Public Datasets in Galaxy

## Summary
Severity: Medium
Advisory: CVE-2024-42351
Aliases: GHSA-5639-cmph-9j4v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-20
Source: https://osv.dev/vulnerability/CVE-2024-42351
Type: osv

## Details
Galaxy is a free, open-source system for analyzing data, authoring workflows, training and education, publishing tools, managing infrastructure, and more. An attacker can potentially replace the contents of public datasets resulting in data loss or tampering. All supported branches of Galaxy (and more back to release_21.05) were amended with the below patch. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://depot.galaxyproject.org/patch/GX-2024-0001/022da344a02bafd604402ac8e253e0014f6e2e08.patch
- https://depot.galaxyproject.org/patch/GX-2024-0001/15060a6cb222f2fcfc687d0f0260f1eb1b9c757b.patch
- https://depot.galaxyproject.org/patch/GX-2024-0001/235f1d8b400708556732b9dda788c919ebf3bb80.patch
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42351.json
- https://github.com/galaxyproject/galaxy/security/advisories/GHSA-5639-cmph-9j4v
- https://nvd.nist.gov/vuln/detail/CVE-2024-42351
