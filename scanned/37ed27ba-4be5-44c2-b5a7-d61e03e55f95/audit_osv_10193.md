# [H] CVE-2017-14227

## Summary
Severity: High
Advisory: CVE-2017-14227
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-09
Source: https://osv.dev/vulnerability/CVE-2017-14227
Type: osv

## Details
In MongoDB libbson 1.7.0, the bson_iter_codewscope function in bson-iter.c miscalculates a bson_utf8_validate length argument, which allows remote attackers to cause a denial of service (heap-based buffer over-read in the bson_utf8_validate function in bson-utf8.c), as demonstrated by bson-to-json.c.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00012.html
- http://www.securityfocus.com/bid/100825
- https://bugzilla.redhat.com/show_bug.cgi?id=1489355
- https://bugzilla.redhat.com/show_bug.cgi?id=1489356
- https://bugzilla.redhat.com/show_bug.cgi?id=1489362
