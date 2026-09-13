# [C] CVE-2018-10574

## Summary
Severity: Critical
Advisory: CVE-2018-10574
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-30
Source: https://osv.dev/vulnerability/CVE-2018-10574
Type: osv

## Details
site/index.php/admin/trees/add/ in BigTree 4.2.22 and earlier allows remote attackers to upload and execute arbitrary PHP code because the BigTreeStorage class in core/inc/bigtree/apis/storage.php does not prevent uploads of .htaccess files.

## References
- https://github.com/bigtreecms/BigTree-CMS/issues/335
- https://github.com/bigtreecms/BigTree-CMS/commit/609bd17728ee1db0487a42d96028d30537528ae8
