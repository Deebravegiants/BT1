# [H] CVE-2017-5923

## Summary
Severity: High
Advisory: CVE-2017-5923
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2017-5923
Type: osv

## Details
libyara/grammar.y in YARA 3.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted rule that is mishandled in the yara_yyparse function.

## References
- http://www.securityfocus.com/bid/98080
- https://github.com/VirusTotal/yara/commit/ab906da53ff2a68c6fd6d1fa73f2b7c7bf0bc636
- https://github.com/VirusTotal/yara/issues/597
