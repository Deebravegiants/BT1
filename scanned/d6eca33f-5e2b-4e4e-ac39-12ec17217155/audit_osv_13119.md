# [H] CVE-2018-17553

## Summary
Severity: High
Advisory: CVE-2018-17553
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-03
Source: https://osv.dev/vulnerability/CVE-2018-17553
Type: osv

## Details
An "Unrestricted Upload of File with Dangerous Type" issue with directory traversal in navigate_upload.php in Naviwebs Navigate CMS 2.8 allows authenticated attackers to achieve remote code execution via a POST request with engine=picnik and id=../../../navigate_info.php.

## References
- https://github.com/NavigateCMS/Navigate-CMS/commit/2bdcb8b3c5bb23851a2115db96585f1ac8cb2d1e
- https://github.com/rapid7/metasploit-framework/pull/10704
- https://www.exploit-db.com/exploits/45561/
