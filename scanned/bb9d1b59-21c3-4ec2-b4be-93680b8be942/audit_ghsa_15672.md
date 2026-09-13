# [H] Apache StreamPark: FreeMarker SSTI RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-vv8h-m63v-53pq
CVE: CVE-2024-29178
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-18
Source: https://github.com/advisories/GHSA-vv8h-m63v-53pq
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=0 <2.1.4

## Details
On versions before 2.1.4, a user could log in and perform a template injection attack resulting in Remote Code Execution on the server, The attacker must successfully log into the system to launch an attack, so this is a moderate-impact vulnerability.

Mitigation:

all users should upgrade to 2.1.4

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29178
- https://github.com/apache/streampark
- https://lists.apache.org/thread/n6dhnl68knpxy80t35qxkkw2691l8sfn
- http://www.openwall.com/lists/oss-security/2024/07/18/1
