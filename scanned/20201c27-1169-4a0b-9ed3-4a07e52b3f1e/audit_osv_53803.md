# [H] CVE-2023-25746

## Summary
Severity: High
Advisory: CVE-2023-25746
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25746
Type: osv

## Details
Memory safety bugs present in Firefox ESR 102.7. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Thunderbird < 102.8 and Firefox ESR < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1544127%2C1762368
