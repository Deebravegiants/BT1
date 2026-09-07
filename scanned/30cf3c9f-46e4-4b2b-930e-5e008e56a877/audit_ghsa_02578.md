# [M] Cross-site Scripting in OpenCRX

## Summary
Severity: Medium
Advisory: GHSA-rwh9-8xx8-4wfm
CVE: CVE-2021-25959
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-30
Source: https://github.com/advisories/GHSA-rwh9-8xx8-4wfm
Type: github-advisory

## Affected
- Maven: `org.opencrx:opencrx-core` — affected >=4.0.0 <5.2.0
- Maven: `org.opencrx:opencrx-core-models` — affected >=4.0.0 <5.2.0
- Maven: `org.opencrx:opencrx-core-config` — affected >=4.0.0 <5.2.0
- Maven: `org.opencrx:opencrx-client` — affected >=4.0.0 <5.2.0
- Maven: `org.opencrx:opencrx-gradle` — affected >=4.0.0 <5.2.0

## Details
In OpenCRX, versions v4.0.0 through v5.1.0 are vulnerable to reflected Cross-site Scripting (XSS), due to unsanitized parameters in the password reset functionality. This allows execution of external javascript files on any user of the openCRX instance.

## References
- https://github.com/opencrx/opencrx/commit/14e75f95e5f56fbe7ee897bdf5d858788072e818
- https://github.com/opencrx/opencrx
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25959
