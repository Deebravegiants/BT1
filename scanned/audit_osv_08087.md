# [H] CVE-2016-10210

## Summary
Severity: High
Advisory: CVE-2016-10210
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2016-10210
Type: osv

## Details
libyara/lexer.l in YARA 3.5.0 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted rule that is mishandled in the yy_get_next_buffer function.

## References
- http://www.securityfocus.com/bid/98077
- https://github.com/VirusTotal/yara/commit/3119b232c9c453c98d8fa8b6ae4e37ba18117cd4
- https://github.com/VirusTotal/yara/issues/576
