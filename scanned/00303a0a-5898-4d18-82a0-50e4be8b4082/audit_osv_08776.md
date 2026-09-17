# [H] CVE-2016-5827

## Summary
Severity: High
Advisory: CVE-2016-5827
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-5827
Type: osv

## Details
The icaltime_from_string function in libical 0.47 and 1.0 allows remote attackers to cause a denial of service (out-of-bounds heap read) via a crafted string to the icalparser_parse_string function.

## References
- http://www.openwall.com/lists/oss-security/2016/06/25/4
- http://www.securityfocus.com/bid/91459
- https://bugzilla.mozilla.org/show_bug.cgi?id=1281043
