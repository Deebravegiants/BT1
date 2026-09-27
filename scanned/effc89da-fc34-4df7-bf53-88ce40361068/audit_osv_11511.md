# [H] CVE-2017-8294

## Summary
Severity: High
Advisory: CVE-2017-8294
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/CVE-2017-8294
Type: osv

## Details
libyara/re.c in the regex component in YARA 3.5.0 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted rule that is mishandled in the yr_re_exec function.

## References
- http://www.securityfocus.com/bid/98072
- https://github.com/VirusTotal/yara/commit/83d799804648c2a0895d40a19835d9b757c6fa4e
- https://github.com/VirusTotal/yara/issues/646
