# [C] CVE-2020-17363

## Summary
Severity: Critical
Advisory: CVE-2020-17363
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-31
Source: https://osv.dev/vulnerability/CVE-2020-17363
Type: osv

## Details
USVN (aka User-friendly SVN) before 1.0.9 allows remote code execution via shell metacharacters in the number_start or number_end parameter to LastHundredRequest (aka lasthundredrequestAction) in the Timeline module. NOTE: this may overlap CVE-2020-25069.

## References
- https://sysdream.com/news/lab/2020-08-12-cve-2020-17363-usvn-remote-code-execution/
