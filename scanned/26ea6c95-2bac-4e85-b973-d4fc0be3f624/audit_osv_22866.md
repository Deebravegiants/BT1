# [M] Ultimate Member Plugin Template class-shortcodes.php load_template pathname traversal

## Summary
Severity: Medium
Advisory: CVE-2022-3966
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-11-13
Source: https://osv.dev/vulnerability/CVE-2022-3966
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in Ultimate Member Plugin up to 2.5.0. This issue affects the function load_template of the file includes/core/class-shortcodes.php of the component Template Handler. The manipulation of the argument tpl leads to pathname traversal. The attack may be initiated remotely. Upgrading to version 2.5.1 is able to address this issue. The name of the patch is e1bc94c1100f02a129721ba4be5fbc44c3d78ec4. It is recommended to upgrade the affected component. The identifier VDB-213545 was assigned to this vulnerability.

## References
- https://github.com/ultimatemember/ultimatemember/releases/tag/2.5.1
- https://vuldb.com/?id.213545
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3966.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3966
- https://github.com/ultimatemember/ultimatemember/commit/e1bc94c1100f02a129721ba4be5fbc44c3d78ec4
