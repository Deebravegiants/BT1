# [H] CVE-2019-12161

## Summary
Severity: High
Advisory: CVE-2019-12161
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-17
Source: https://osv.dev/vulnerability/CVE-2019-12161
Type: osv

## Details
WPO WebPageTest 19.04 allows SSRF because ValidateURL in www/runtest.php does not consider octal encoding of IP addresses (such as 0300.0250 as a replacement for 192.168).

## References
- https://bugzilla.mozilla.org/show_bug.cgi?id=1550366
