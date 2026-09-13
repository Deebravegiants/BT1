# [C] CVE-2016-7790

## Summary
Severity: Critical
Advisory: CVE-2016-7790
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/CVE-2016-7790
Type: osv

## Details
Exponent CMS 2.3.9 suffers from a remote code execution vulnerability in /install/index.php. An attacker can upload 'php' file to the website through uploader_paste.php, then overwrite /framework/conf/config.php, which leads to arbitrary code execution.

## References
- http://www.securityfocus.com/bid/93119
- http://www.openwall.com/lists/oss-security/2016/09/22/6
