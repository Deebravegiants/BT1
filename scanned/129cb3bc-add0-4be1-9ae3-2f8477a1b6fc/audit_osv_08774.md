# [M] CVE-2016-5825

## Summary
Severity: Medium
Advisory: CVE-2016-5825
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-5825
Type: osv

## Details
The icalparser_parse_string function in libical 0.47 and 1.0 allows remote attackers to cause a denial of service (out-of-bounds heap read) via a crafted ics file.

## References
- http://www.openwall.com/lists/oss-security/2016/06/25/4
- http://www.securityfocus.com/bid/91459
- https://bugzilla.mozilla.org/show_bug.cgi?id=1280832
