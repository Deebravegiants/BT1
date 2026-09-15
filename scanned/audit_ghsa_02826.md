# [M] Email relay in Apache Traffic Control

## Summary
Severity: Medium
Advisory: GHSA-gw97-f6h8-gm94
CVE: CVE-2021-42009
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-10-13
Source: https://github.com/advisories/GHSA-gw97-f6h8-gm94
Type: github-advisory

## Affected
- Go: `github.com/apache/trafficcontrol` — affected >=0 <5.1.3

## Details
An authenticated Apache Traffic Control Traffic Ops user with Portal-level privileges can send a request with a specially-crafted email subject to the /deliveryservices/request Traffic Ops endpoint to send an email, from the Traffic Ops server, with an arbitrary body to an arbitrary email address. Apache Traffic Control 5.1.x users should upgrade to 5.1.3 or 6.0.0. 4.1.x users should upgrade to 5.1.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42009
- https://github.com/apache/trafficcontrol
- https://lists.apache.org/thread.html/r78d471d8a4fd268a4c5ae6c47327c09d9d4b4467c31da2c97422febb@%3Cdev.trafficcontrol.apache.org%3E
- https://lists.apache.org/thread.html/r7dfa9a89b39d06caeeeb7b5cdc41b3493a9b86cc6cfa059d3f349d87@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/re384fd0f44c6d230f31376153c6e8b59e4a669f927c1533d06d702af%40%3Cdev.trafficcontrol.apache.org%3E
- https://lists.apache.org/thread.html/rf0481b9e38ece1ece458d3ce7b2d671df819e3555597f31fc34f084e%40%3Ccommits.trafficcontrol.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/10/12/1
