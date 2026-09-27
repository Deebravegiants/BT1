# [M] kalcaddle KodExplorer API Endpoint unrestricted upload

## Summary
Severity: Medium
Advisory: CVE-2023-6850
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-16
Source: https://osv.dev/vulnerability/CVE-2023-6850
Type: osv

## Details
A vulnerability was found in kalcaddle KodExplorer up to 4.51.03. It has been declared as critical. This vulnerability affects unknown code of the file /index.php?pluginApp/to/yzOffice/getFile of the component API Endpoint Handler. The manipulation of the argument path/file leads to unrestricted upload. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 4.52.01 is able to address this issue. The patch is identified as 5cf233f7556b442100cf67b5e92d57ceabb126c6. It is recommended to upgrade the affected component. VDB-248218 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6850.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6850
- https://vuldb.com/?id.248218
- https://vuldb.com/?ctiid.248218
- https://github.com/kalcaddle/KodExplorer/commit/5cf233f7556b442100cf67b5e92d57ceabb126c6
- https://github.com/kalcaddle/KodExplorer/releases/tag/4.52.01
- https://note.zhaoj.in/share/L38RNzUOwOtN
