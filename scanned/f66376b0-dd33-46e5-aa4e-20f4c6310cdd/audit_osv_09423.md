# [C] CVE-2016-9835

## Summary
Severity: Critical
Advisory: CVE-2016-9835
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-05
Source: https://osv.dev/vulnerability/CVE-2016-9835
Type: osv

## Details
Directory traversal vulnerability in file "jcss.php" in Zikula 1.3.x before 1.3.11 and 1.4.x before 1.4.4 on Windows allows a remote attacker to launch a PHP object injection by uploading a serialized file.

## References
- http://www.securityfocus.com/bid/95005
- https://github.com/zikula/core/blob/1.3/CHANGELOG-1.3.md
- https://github.com/zikula/core/blob/1.4/CHANGELOG-1.4.md
- https://github.com/zikula/core/issues/3237
