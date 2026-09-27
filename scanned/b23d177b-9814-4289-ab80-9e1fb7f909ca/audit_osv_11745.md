# [H] CVE-2017-9465

## Summary
Severity: High
Advisory: CVE-2017-9465
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-06-06
Source: https://osv.dev/vulnerability/CVE-2017-9465
Type: osv

## Details
The yr_arena_write_data function in YARA 3.6.1 allows remote attackers to cause a denial of service (buffer over-read and application crash) or obtain sensitive information from process memory via a crafted file that is mishandled in the yr_re_fast_exec function in libyara/re.c and the _yr_scan_match_callback function in libyara/scan.c.

## References
- https://github.com/VirusTotal/yara/commit/992480c30f75943e9cd6245bb2015c7737f9b661
- https://github.com/VirusTotal/yara/issues/678
