# [H] CVE-2018-1000867

## Summary
Severity: High
Advisory: CVE-2018-1000867
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000867
Type: osv

## Details
WeBid version up to current version 1.2.2 contains a SQL Injection vulnerability in All five yourauctions*.php scripts that can result in Database Read via Blind SQL Injection. This attack appear to be exploitable via HTTP Request. This vulnerability appears to have been fixed in after commit 256a5f9d3eafbc477dcf77c7682446cc4b449c7f.

## References
- http://bugs.webidsupport.com/view.php?id=647
- https://github.com/renlok/WeBid/commit/256a5f9d3eafbc477dcf77c7682446cc4b449c7f
- https://telekomsecurity.github.io/assets/advisories/20181108_WeBid_Multiple_Vulnerabilities.txt
