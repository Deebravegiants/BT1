# [H] CVE-2018-1000882

## Summary
Severity: High
Advisory: CVE-2018-1000882
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000882
Type: osv

## Details
WeBid version up to current version 1.2.2 contains a Directory Traversal vulnerability in getthumb.php that can result in Arbitrary Image File Read. This attack appear to be exploitable via HTTP GET Request. This vulnerability appears to have been fixed in after commit 256a5f9d3eafbc477dcf77c7682446cc4b449c7f.

## References
- http://bugs.webidsupport.com/view.php?id=646
- https://github.com/renlok/WeBid/commit/256a5f9d3eafbc477dcf77c7682446cc4b449c7f
- https://telekomsecurity.github.io/assets/advisories/20181108_WeBid_Multiple_Vulnerabilities.txt
