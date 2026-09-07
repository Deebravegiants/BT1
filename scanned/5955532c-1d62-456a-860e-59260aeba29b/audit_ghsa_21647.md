# [H] Deserialization of untrusted data in Apache Cayenne

## Summary
Severity: High
Advisory: GHSA-c58c-w527-h77p
CVE: CVE-2022-24289
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-c58c-w527-h77p
Type: github-advisory

## Affected
- Maven: `org.apache.cayenne:cayenne-server` — affected >=0 <4.1.1

## Details
Hessian serialization is a network protocol that supports object-based transmission. Apache Cayenne's optional Remote Object Persistence (ROP) feature is a web services-based technology that provides object persistence and query functionality to 'remote' applications. In Apache Cayenne 4.1 and earlier, running on non-current patch versions of Java, an attacker with client access to Cayenne ROP can transmit a malicious payload to any vulnerable third-party dependency on the server. This can result in arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24289
- https://lists.apache.org/thread/zthjy83t3o66x7xcbygn2vg3yjvlc9vc
- http://www.openwall.com/lists/oss-security/2022/02/11/1
