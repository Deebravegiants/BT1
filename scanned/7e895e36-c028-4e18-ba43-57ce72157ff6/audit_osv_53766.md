# [M] CVE-2023-23603

## Summary
Severity: Medium
Advisory: CVE-2023-23603
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-23603
Type: osv

## Details
Regular expressions used to filter out forbidden properties and values from style directives in calls to `console.log` weren't accounting for external URLs. Data could then be potentially exfiltrated from the browser. This vulnerability affects Firefox < 109, Firefox ESR < 102.7, and Thunderbird < 102.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-01/
- https://www.mozilla.org/security/advisories/mfsa2023-02/
- https://www.mozilla.org/security/advisories/mfsa2023-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1800832
