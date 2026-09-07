# [M] Vaadin vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-7wwv-79xw-rvvg
CVE: CVE-2025-15022
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-7wwv-79xw-rvvg
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-server` — affected >=7.0.0 <7.7.50
- Maven: `com.vaadin:vaadin-server` — affected >=8.0.0 <8.30.0
- Maven: `com.vaadin:vaadin` — affected >=23.1.0 <23.6.6
- Maven: `com.vaadin:vaadin` — affected >=24.0.0 <24.8.14
- Maven: `com.vaadin:vaadin` — affected >=24.9.0 <24.9.7
- Maven: `com.vaadin:vaadin-spreadsheet-flow` — affected >=23.1.0 <23.6.6
- Maven: `com.vaadin:vaadin-spreadsheet-flow` — affected >=24.0.0 <24.8.14
- Maven: `com.vaadin:vaadin-spreadsheet-flow` — affected >=24.9.0 <24.9.7

## Details
Action captions in Vaadin accept HTML by default but were not sanitized, potentially allowing Cross-site Scripting (XSS) if caption content is derived from user input.

In Vaadin Framework 7 and 8, the Action class is a general-purpose class that may be used by multiple components. The fixed versions sanitize captions by default and provide an API to explicitly enable HTML content mode for backwards compatibility.

In Vaadin 23 and newer, the Action class is only used by the Spreadsheet component. The fixed versions sanitize HTML using Jsoup with a relaxed safelist.

Vaadin 14 is not affected as Spreadsheet component was not supported.

Users of affected versions should apply the following mitigation or upgrade. Releases that have fixed this issue include:

Product version
Vaadin 7.0.0 - 7.7.49
Vaadin 8.0.0 - 8.29.1
Vaadin 23.1.0 - 23.6.5
Vaadin 24.0.0 - 24.8.13
Vaadin 24.9.0 - 24.9.6

Mitigation
Upgrade to 7.7.50
Upgrade to 8.30.0
Upgrade to 23.6.6
Upgrade to 24.8.14 or 24.9.7
Upgrade to 25.0.0 or newer

Artifacts     Maven coordinatesVulnerable versionsFixed versioncom.vaadin:vaadin-server
7.0.0 - 7.7.49
≥7.7.50
com.vaadin:vaadin-server
8.0.0 - 8.29.1
≥8.30.0
com.vaadin:vaadin
23.1.0 - 23.6.5
≥23.6.6
com.vaadin:vaadin24.0.0 - 24.8.13
≥24.8.14
com.vaadin:vaadin24.9.0 - 24.9.6
≥24.9.7
com.vaadin:vaadin-spreadsheet-flow
23.1.0 - 23.6.5
≥23.6.6
com.vaadin:vaadin-spreadsheet-flow
24.0.0 - 24.8.13
≥24.8.14
com.vaadin:vaadin-spreadsheet-flow
24.9.0 - 24.9.6
≥24.9.7

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-15022
- https://github.com/vaadin/flow-components/pull/8285
- https://github.com/vaadin/flow-components/commit/71046aa3dd08be0907bd03140c33131b94f6e99c
- https://github.com/vaadin/flow-components
- https://vaadin.com/security/cve-2025-15022
