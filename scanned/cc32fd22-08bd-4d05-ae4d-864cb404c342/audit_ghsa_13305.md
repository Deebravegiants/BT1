# [C] rabbitmq-connector plugin module in Apache EventMesh platforms allows attackers to send controlled message

## Summary
Severity: Critical
Advisory: GHSA-fj8f-56wc-q36r
CVE: CVE-2023-26512
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-17
Source: https://github.com/advisories/GHSA-fj8f-56wc-q36r
Type: github-advisory

## Affected
- Maven: `org.apache.eventmesh:eventmesh-connector-rabbitmq` — affected >=1.7.0

## Details
CWE-502 Deserialization of Untrusted Data at the rabbitmq-connector plugin module in Apache EventMesh (incubating) V1.7.0\V1.8.0 on windows\linux\mac os e.g. platforms allows attackers to send controlled message and 

remote code execute via rabbitmq messages. Users can use the code under the master branch in project repo to fix this issue,  the new version is set to be released as soon as possible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26512
- https://lists.apache.org/thread/zb1d62wh8o8pvntrnx4t1hj8vz0pm39p
