# [H] CVE-2026-34352

## Summary
Severity: High
Advisory: CVE-2026-34352
CVSS: 8.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-34352
Type: osv

## Details
In TigerVNC before 1.16.2, Image.cxx in x0vncserver allows other users to observe or manipulate the screen contents, or cause an application crash, because of incorrect permissions.

## References
- https://groups.google.com/g/tigervnc-announce/c/anHL9WLshLI
- https://sourceforge.net/projects/tigervnc/files/stable/1.16.2
- https://www.openwall.com/lists/oss-security/2026/03/26/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34352.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34352
- https://github.com/TigerVNC/tigervnc/issues/2079
- https://github.com/TigerVNC/tigervnc/commit/0b5cab169d847789efa54459a87659d3fd484393
