# [H] CVE-2017-9304

## Summary
Severity: High
Advisory: CVE-2017-9304
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-31
Source: https://osv.dev/vulnerability/CVE-2017-9304
Type: osv

## Details
libyara/re.c in the regexp module in YARA 3.5.0 allows remote attackers to cause a denial of service (stack consumption) via a crafted rule that is mishandled in the _yr_re_emit function.

## References
- https://github.com/VirusTotal/yara/commit/925bcf3c3b0a28b5b78e25d9efda5c0bf27ae699
- https://github.com/VirusTotal/yara/issues/674
