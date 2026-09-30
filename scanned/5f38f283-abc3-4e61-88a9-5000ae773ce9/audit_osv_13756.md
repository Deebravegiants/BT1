# [H] CVE-2018-25094

## Summary
Severity: High
Advisory: CVE-2018-25094
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-03
Source: https://osv.dev/vulnerability/CVE-2018-25094
Type: osv

## Details
A vulnerability was found in ระบบบัญชีออนไลน์ Online Accounting System up to 1.4.0 and classified as problematic. This issue affects some unknown processing of the file ckeditor/filemanager/browser/default/image.php. The manipulation of the argument fid with the input ../../../etc/passwd leads to path traversal: '../filedir'. The exploit has been disclosed to the public and may be used. Upgrading to version 2.0.0 is able to address this issue. The identifier of the patch is 9d9618422b980335bb30be612ea90f4f56cb992c. It is recommended to upgrade the affected component. The identifier VDB-246641 was assigned to this vulnerability.

## References
- https://vuldb.com/?id.246641
- https://vuldb.com/?ctiid.246641
- https://github.com/59160781/project/commit/9d9618422b980335bb30be612ea90f4f56cb992c
