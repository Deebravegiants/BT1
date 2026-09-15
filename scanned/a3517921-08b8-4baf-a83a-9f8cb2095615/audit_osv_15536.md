# [M] CVE-2019-16985

## Summary
Severity: Medium
Advisory: CVE-2019-16985
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/CVE-2019-16985
Type: osv

## Details
In FusionPBX up to v4.5.7, the file app\xml_cdr\xml_cdr_delete.php uses an unsanitized "rec" variable coming from the URL, which is base64 decoded and allows deletion of any file of the system.

## References
- https://resp3ctblog.wordpress.com/2019/10/19/fusionpbx-path-traversal-1/
- https://github.com/fusionpbx/fusionpbx/commit/284b0a91968f126fd6be0a486a84e065926905ca
