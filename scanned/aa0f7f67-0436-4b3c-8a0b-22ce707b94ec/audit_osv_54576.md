# [H] CVE-2024-11699

## Summary
Severity: High
Advisory: CVE-2024-11699
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-11699
Type: osv

## Details
Memory safety bugs present in Firefox 132, Firefox ESR 128.4, and Thunderbird 128.4. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 133, Firefox ESR < 128.5, Thunderbird < 133, and Thunderbird < 128.5.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00029.html
- https://www.mozilla.org/security/advisories/mfsa2024-63/
- https://www.mozilla.org/security/advisories/mfsa2024-64/
- https://www.mozilla.org/security/advisories/mfsa2024-67/
- https://www.mozilla.org/security/advisories/mfsa2024-68/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1880582%2C1929911
