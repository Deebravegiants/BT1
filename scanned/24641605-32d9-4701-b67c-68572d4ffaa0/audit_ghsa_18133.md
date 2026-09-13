# [M] Vaadin Framework possible file bypass via upload validation on the server-side

## Summary
Severity: Medium
Advisory: GHSA-9gfh-4fwj-w3rj
CVE: CVE-2025-9467
CWE: CWE-20, CWE-434
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N/S:N/AU:N/R:U/V:D/RE:L/U:Green (CVSS_V4)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-9gfh-4fwj-w3rj
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-server` — affected >=7.0.0 <7.7.48
- Maven: `com.vaadin:vaadin-server` — affected >=8.0.0 <8.28.2

## Details
### Description
When the Vaadin Upload's start listener is used to validate metadata about an incoming upload, it is possible to bypass the upload validation. Users of affected versions should apply the upgrade to a more recent Vaadin version.

## References
- https://github.com/vaadin/framework/security/advisories/GHSA-9gfh-4fwj-w3rj
- https://nvd.nist.gov/vuln/detail/CVE-2025-9467
- https://github.com/vaadin/flow-components/pull/7616
- https://github.com/vaadin/flow-components/commit/bfe9e507cdcc5d90a2312c8f0162f798a29ba635
- https://github.com/vaadin/framework
- https://vaadin.com/security/cve-2025-9467
