# [M] Improper Handling of Exceptional Conditions and Origin Validation Error in Eclipse Paho Java client library

## Summary
Severity: Medium
Advisory: GHSA-63qc-p2x4-9fgf
CVE: CVE-2019-11777
CWE: CWE-346, CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-09-17
Source: https://github.com/advisories/GHSA-63qc-p2x4-9fgf
Type: github-advisory

## Affected
- Maven: `org.eclipse.paho:org.eclipse.paho.client.mqttv3` — affected >=0 <1.2.1

## Details
In the Eclipse Paho Java client library version 1.2.0, when connecting to an MQTT server using TLS and setting a host name verifier, the result of that verification is not checked. This could allow one MQTT server to impersonate another and provide the client library with incorrect information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11777
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=549934
