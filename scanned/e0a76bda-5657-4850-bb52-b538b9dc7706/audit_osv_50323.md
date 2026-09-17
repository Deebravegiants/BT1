# [M] CVE-2020-12405

## Summary
Severity: Medium
Advisory: CVE-2020-12405
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12405
Type: osv

## Details
When browsing a malicious page, a race condition in our SharedWorkerService could occur and lead to a potentially exploitable crash. This vulnerability affects Thunderbird < 68.9.0, Firefox < 77, and Firefox ESR < 68.9.

## References
- https://usn.ubuntu.com/4421-1/
- https://www.mozilla.org/security/advisories/mfsa2020-20/
- https://www.mozilla.org/security/advisories/mfsa2020-21/
- https://www.mozilla.org/security/advisories/mfsa2020-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1631618
