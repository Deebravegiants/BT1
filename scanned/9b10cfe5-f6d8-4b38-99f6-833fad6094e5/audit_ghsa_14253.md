# [M] RosarioSIS improper access control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g66v-3v62-g375
CVE: CVE-2023-2202
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-g66v-3v62-g375
Type: github-advisory

## Affected
- Packagist: `francoisjacquet/rosariosis` — affected >=0 <10.9.3

## Details
RosarioSIS prior to version 10.9.3 has a vulnerability that allows a user to return to a page containing personally identifiable information (PII) and sensitive information even after logging out of the application by using the browser's back button.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2202
- https://github.com/francoisjacquet/rosariosis/commit/6433946abfb34324616e833b1c00d0b2450753be
- https://github.com/francoisjacquet/rosariosis
- https://github.com/francoisjacquet/rosariosis/compare/v10.9.2...v10.9.3
- https://huntr.dev/bounties/efe6ef47-d17c-4773-933a-4836c32db85c
