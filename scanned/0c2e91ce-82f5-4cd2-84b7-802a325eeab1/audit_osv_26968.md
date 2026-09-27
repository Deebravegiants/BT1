# [H] kalcaddle kodbox index.class.php check command injection

## Summary
Severity: High
Advisory: CVE-2023-6848
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-16
Source: https://osv.dev/vulnerability/CVE-2023-6848
Type: osv

## Details
A vulnerability was found in kalcaddle kodbox up to 1.48. It has been declared as critical. Affected by this vulnerability is the function check of the file plugins/officeViewer/controller/libreOffice/index.class.php. The manipulation of the argument soffice leads to command injection. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 1.48.04 is able to address this issue. The identifier of the patch is 63a4d5708d210f119c24afd941d01a943e25334c. It is recommended to upgrade the affected component. The identifier VDB-248209 was assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6848.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6848
- https://vuldb.com/?id.248209
- https://vuldb.com/?ctiid.248209
- https://github.com/kalcaddle/kodbox/commit/63a4d5708d210f119c24afd941d01a943e25334c
- https://github.com/kalcaddle/kodbox/releases/tag/1.48.04
- https://note.zhaoj.in/share/pf838kAzQyTQ
