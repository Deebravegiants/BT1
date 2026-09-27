# [H] CVE-2023-6873

## Summary
Severity: High
Advisory: CVE-2023-6873
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6873
Type: osv

## Details
Memory safety bugs present in Firefox 120. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 121.

## References
- https://www.debian.org/security/2023/dsa-5582
- https://www.mozilla.org/security/advisories/mfsa2023-56/
- https://lists.debian.org/debian-lts-announce/2023/12/msg00021.html
- https://security.gentoo.org/glsa/202401-10
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1855327%2C1862089%2C1862723
