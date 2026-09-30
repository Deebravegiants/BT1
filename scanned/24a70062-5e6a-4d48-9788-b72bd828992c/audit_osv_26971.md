# [M] kalcaddle KodExplorer ZIP Archive app.php unzipList code injection

## Summary
Severity: Medium
Advisory: CVE-2023-6851
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-16
Source: https://osv.dev/vulnerability/CVE-2023-6851
Type: osv

## Details
A vulnerability was found in kalcaddle KodExplorer up to 4.51.03. It has been rated as critical. This issue affects the function unzipList of the file plugins/zipView/app.php of the component ZIP Archive Handler. The manipulation leads to code injection. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 4.52.01 is able to address this issue. The patch is named 5cf233f7556b442100cf67b5e92d57ceabb126c6. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-248219.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6851.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6851
- https://vuldb.com/?id.248219
- https://vuldb.com/?ctiid.248219
- https://github.com/kalcaddle/KodExplorer/commit/5cf233f7556b442100cf67b5e92d57ceabb126c6
- https://github.com/kalcaddle/KodExplorer/releases/tag/4.52.01
- https://note.zhaoj.in/share/D44UjzoFXYfi
