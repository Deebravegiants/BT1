# [H] CVE-2017-5924

## Summary
Severity: High
Advisory: CVE-2017-5924
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2017-5924
Type: osv

## Details
libyara/grammar.y in YARA 3.5.0 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted rule that is mishandled in the yr_compiler_destroy function.

## References
- http://www.securityfocus.com/bid/98075
- https://github.com/VirusTotal/yara/commit/7f02eca670f29c00a1d2c305e96febae6ce5d37b
- https://github.com/VirusTotal/yara/issues/593
