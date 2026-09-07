# [M] Denial of service in DataCommunicator class in Vaadin 8

## Summary
Severity: Medium
Advisory: GHSA-j23j-q57m-63v3
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-10-13
Source: https://github.com/advisories/GHSA-j23j-q57m-63v3
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-server` — affected >=8.0.0 <8.14.1

## Details
Missing check in `DataCommunicator` class in `com.vaadin:vaadin-server` versions 8.0.0 through 8.14.0 (Vaadin 8.0.0 through 8.14.0) allows authenticated network attacker to cause heap exhaustion by requesting too many rows of data.

## References
- https://github.com/vaadin/framework/security/advisories/GHSA-j23j-q57m-63v3
- https://github.com/vaadin/framework/pull/12415
- https://vaadin.com/security/cve-2021-33609
