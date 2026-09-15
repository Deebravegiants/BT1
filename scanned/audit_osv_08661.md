# [H] CVE-2016-5095

## Summary
Severity: High
Advisory: CVE-2016-5095
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5095
Type: osv

## Details
Integer overflow in the php_escape_html_entities_ex function in ext/standard/html.c in PHP before 5.5.36 and 5.6.x before 5.6.22 allows remote attackers to cause a denial of service or possibly have unspecified other impact by triggering a large output string from a FILTER_SANITIZE_FULL_SPECIAL_CHARS filter_var call.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-5094.

## References
- http://www.securityfocus.com/bid/92144
- https://bugs.php.net/bug.php?id=72135
- https://gist.github.com/8ef775c117d84ff15185953990a28576
- http://php.net/ChangeLog-5.php
- http://www.debian.org/security/2016/dsa-3602
- http://www.openwall.com/lists/oss-security/2016/05/26/3
