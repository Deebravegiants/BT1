# [M] DHIS2 Core Improper Access Control with Category Option Combination sharing in /api/trackedEntityInstance and /api/events

## Summary
Severity: Medium
Advisory: CVE-2023-32060
Aliases: GHSA-7pwm-6rh2-2388
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-09
Source: https://osv.dev/vulnerability/CVE-2023-32060
Type: osv

## Details
DHIS2 Core contains the service layer and Web API for DHIS2, an information system for data capture. Starting in the 2.35 branch and prior to versions 2.36.13, 2.37.8, 2.38.2, and 2.39.0, when the Category Option Combination Sharing settings are configured to control access to specific tracker program events or program stages, the `/trackedEntityInstances` and `/events` API endpoints may include all events regardless of the sharing settings applied to the category option combinations. When this specific configuration is present, users may have access to events which they should not be able to see based on the sharing settings of the category options.  The events will not appear in the user interface for web-based Tracker Capture or Capture applications, but if the Android Capture App is used they will be displayed to the user. Versions 2.36.13, 2.37.8, 2.38.2, and 2.39.0 contain a fix for this issue. No workaround is known.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32060.json
- https://github.com/dhis2/dhis2-core/security/advisories/GHSA-7pwm-6rh2-2388
- https://nvd.nist.gov/vuln/detail/CVE-2023-32060
