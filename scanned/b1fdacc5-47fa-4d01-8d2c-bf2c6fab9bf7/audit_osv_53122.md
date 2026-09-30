# [M] CVE-2022-29916

## Summary
Severity: Medium
Advisory: CVE-2022-29916
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-29916
Type: osv

## Details
Firefox behaved slightly differently for already known resources when loading CSS resources involving CSS variables. This could have been used to probe the browser history. This vulnerability affects Thunderbird < 91.9, Firefox ESR < 91.9, and Firefox < 100.

## References
- https://bugzilla.mozilla.org/show_bug.cgi?id=1760674
- https://www.mozilla.org/security/advisories/mfsa2022-18/
- https://www.mozilla.org/security/advisories/mfsa2022-16/
- https://www.mozilla.org/security/advisories/mfsa2022-17/
