# [M] ILIAS Arbitrary File Read via SOAP addFile

## Summary
Severity: Medium
Advisory: CVE-2026-82877
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82877
Type: osv

## Details
ILIAS before versions 9.22, 10.10, and 11.3 contains an arbitrary file read vulnerability in the SOAP addFile method that allows authenticated users to read server files by supplying crafted XML with COPY-mode imports. Attackers can construct absolute file paths through an unsandboxed import directory and retrieve sensitive files including configuration files containing database credentials and setup passwords.

## References
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=934
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=935
- https://docu.ilias.de/ilias.php?baseClass=ilrepositorygui&cmdNode=wy:ll:6t&cmdClass=ilBlogPostingGUI&cmd=previewFullscreen&ref_id=15821&blpg=936
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82877.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82877
- https://www.vulncheck.com/advisories/ilias-arbitrary-file-read-via-soap-addfile
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225630&ref_id=35
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225631&ref_id=35
- https://docu.ilias.de/ilias.php?baseClass=illmpresentationgui&obj_id=225632&ref_id=35
- https://github.com/ILIAS-eLearning/ILIAS
