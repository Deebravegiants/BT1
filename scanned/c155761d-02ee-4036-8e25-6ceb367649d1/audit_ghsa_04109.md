# [H] Cleartext Transmission of Sensitive Information, Inclusion of Functionality from Untrusted Control Sphere , and Download of Code Without Integrity Check in Eclipse hawkBit 

## Summary
Severity: High
Advisory: GHSA-jwqm-c9f2-2cq3
CVE: CVE-2019-10240
CWE: CWE-319, CWE-494, CWE-829
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-15
Source: https://github.com/advisories/GHSA-jwqm-c9f2-2cq3
Type: github-advisory

## Affected
- Maven: `org.eclipse.hawkbit:hawkbit-autoconfigure` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-ui` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-parent` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-starters` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-boot-starter` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-update-server` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-boot-starter-mgmt-ui` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-boot-starter-mgmt-api` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-boot-starter-dmf-api` — affected >=0 <0.3.0M2
- Maven: `org.eclipse.hawkbit:hawkbit-boot-starter-ddi-api` — affected >=0 <0.3.0M2

## Details
Eclipse hawkBit versions prior to 0.3.0M2 resolved Maven build artifacts for the Vaadin based UI over HTTP instead of HTTPS. Any of these dependent artifacts could have been maliciously compromised by a MITM attack. Hence produced build artifacts of hawkBit might be infected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10240
- https://github.com/advisories/GHSA-jwqm-c9f2-2cq3
