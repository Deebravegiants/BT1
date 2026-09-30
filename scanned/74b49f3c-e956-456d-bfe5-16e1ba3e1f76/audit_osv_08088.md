# [H] CVE-2016-10211

## Summary
Severity: High
Advisory: CVE-2016-10211
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2016-10211
Type: osv

## Details
libyara/grammar.y in YARA 3.5.0 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted rule that is mishandled in the yr_parser_lookup_loop_variable function.

## References
- http://www.securityfocus.com/bid/98078
- https://github.com/VirusTotal/yara/commit/890c3f850293176c0e996a602ffa88b315f4e98f
- https://github.com/VirusTotal/yara/issues/575
