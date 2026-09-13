# [M] rmountjoy92 DashMachine delete_file path traversal

## Summary
Severity: Medium
Advisory: CVE-2023-6900
CVSS: 4.6 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-12-17
Source: https://osv.dev/vulnerability/CVE-2023-6900
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in rmountjoy92 DashMachine 0.5-4. Affected by this issue is some unknown functionality of the file /settings/delete_file. The manipulation of the argument file leads to path traversal: '../filedir'. The exploit has been disclosed to the public and may be used. VDB-248258 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6900.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6900
- https://vuldb.com/?id.248258
- https://vuldb.com/?ctiid.248258
- https://treasure-blarney-085.notion.site/DashMachine-Arbitrary-File-Deletion-ab44f2fe68e843c393ae9e0c1d487676
