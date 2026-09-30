# [H] CVE-2017-9443

## Summary
Severity: High
Advisory: CVE-2017-9443
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9443
Type: osv

## Details
BigTree CMS through 4.2.18 allows remote authenticated users to conduct SQL injection attacks via a crafted tables object in manifest.json in an uploaded package. This issue exists in core\admin\modules\developer\extensions\install\process.php and core\admin\modules\developer\packages\install\process.php. NOTE: the vendor states "You must implicitly trust any package or extension you install as they all have the ability to write PHP files.

## References
- https://github.com/bigtreecms/BigTree-CMS/issues/292
