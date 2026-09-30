# [C] CVE-2022-31747

## Summary
Severity: Critical
Advisory: CVE-2022-31747
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-31747
Type: osv

## Details
Mozilla developers Andrew McCreight, Nicolas B. Pierron, and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 100 and Firefox ESR 91.9. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Thunderbird < 91.10, Firefox < 101, and Firefox ESR < 91.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-20/
- https://www.mozilla.org/security/advisories/mfsa2022-21/
- https://www.mozilla.org/security/advisories/mfsa2022-22/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1760765%2C1765610%2C1766283%2C1767365%2C1768559%2C1768734
