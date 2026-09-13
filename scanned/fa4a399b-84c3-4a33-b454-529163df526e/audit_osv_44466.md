# [C] ILIAS Arbitrary SQL Injection via Repository Trash Table Sort Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-82538
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-82538
Type: osv

## Details
ILIAS before versions 9.22, 10.10, and 11.3 contains a SQL injection vulnerability in the repository trash table where the table navigation sort field from HTTP requests is passed directly into the ORDER BY clause of a SQL query without validation against declared sortable columns. Authenticated users with write permission on any container can inject arbitrary SQL through the sort parameter, and because multi-statement execution is enabled in the database layer, stacked queries enable full database read and write access as well as administrator account takeover.

## References
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=934
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=935
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=936
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82538.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82538
- https://www.vulncheck.com/advisories/ilias-arbitrary-file-read-via-soap-addfile
- https://www.vulncheck.com/advisories/ilias-arbitrary-sql-injection-via-repository-trash-table-sort-parameter
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225630&ref_id=35
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225631&ref_id=35
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225632&ref_id=35
- https://github.com/ILIAS-eLearning/ILIAS
