# [H] kalcaddle kodbox app.php cover server-side request forgery

## Summary
Severity: High
Advisory: CVE-2023-6849
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-16
Source: https://osv.dev/vulnerability/CVE-2023-6849
Type: osv

## Details
A vulnerability was found in kalcaddle kodbox up to 1.48. It has been rated as critical. Affected by this issue is the function cover of the file plugins/fileThumb/app.php. The manipulation of the argument path leads to server-side request forgery. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 1.48.04 is able to address this issue. The patch is identified as 63a4d5708d210f119c24afd941d01a943e25334c. It is recommended to upgrade the affected component. VDB-248210 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6849.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6849
- https://vuldb.com/?id.248210
- https://vuldb.com/?ctiid.248210
- https://github.com/kalcaddle/kodbox/commit/63a4d5708d210f119c24afd941d01a943e25334c
- https://github.com/kalcaddle/kodbox/releases/tag/1.48.04
- https://note.zhaoj.in/share/jSsPAWT1pKsq
