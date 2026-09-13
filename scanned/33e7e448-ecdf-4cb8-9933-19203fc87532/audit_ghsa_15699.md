# [M] Apache StreamPark: Information leakage vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hcf8-5j78-887v
CVE: CVE-2024-29120
CWE: CWE-212, CWE-922
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-hcf8-5j78-887v
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=2.0.0 <2.1.4

## Details
In Streampark (version < 2.1.4), when a user logged in successfully, the Backend service would return "Authorization" as the front-end authentication credential.  User can use this credential to request other users' information, including the administrator's username, password, salt value, etc. 

Mitigation:

all users should upgrade to 2.1.4

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29120
- https://github.com/apache/incubator-streampark
- https://lists.apache.org/thread/y3oqz7l8vd7jxxx3z2khgl625nvfr60j
- http://www.openwall.com/lists/oss-security/2024/07/17/4
