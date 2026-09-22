# [H] CVE-2016-10751

## Summary
Severity: High
Advisory: CVE-2016-10751
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-24
Source: https://osv.dev/vulnerability/CVE-2016-10751
Type: osv

## Details
osClass 3.6.1 allows oc-admin/plugins.php Directory Traversal via the plugin parameter. This is exploitable for remote PHP code execution because an administrator can upload an image that contains PHP code in the EXIF data via index.php?page=ajax&action=ajax_upload.

## References
- https://blog.ripstech.com/2016/osclass-remote-code-execution-via-image-file/
- https://demo.ripstech.com/projects/osclass_3.6.1
