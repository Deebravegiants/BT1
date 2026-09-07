# [M] Baremetrics date range picker vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-465f-mxxh-grc4
CVE: CVE-2021-32859
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-465f-mxxh-grc4
Type: github-advisory

## Affected
- npm: `baremetrics-calendar` — affected >=0

## Details
The Baremetrics date range picker is a solution for selecting both date ranges and single dates from a single calender view. Versions 1.0.14 and prior are prone to cross-site scripting (XSS) when handling untrusted `placeholder` entries. An attacker who is able to influence the field `placeholder` when creating a `Calendar` instance is able to supply arbitrary `html` or `javascript` that will be rendered in the context of a user leading to XSS. There are no known patches for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32859
- https://github.com/Baremetrics/calendar
- https://github.com/Baremetrics/calendar/blob/240c20134ffbf0f0f246a50feff2be1ff19cf349/public/js/Calendar.js#L724
- https://securitylab.github.com/advisories/GHSL-2021-1042_Baremetrics_Date_Range_Picker
