# [H] Apache Camel K: Kubernetes namespace authorized users can create a Build resource

## Summary
Severity: High
Advisory: GHSA-q8ch-jx67-q52x
CVE: CVE-2026-45760
CWE: CWE-610, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-q8ch-jx67-q52x
Type: github-advisory

## Affected
- Go: `github.com/apache/camel-k/v2` — affected >=0 <2.8.1
- Go: `github.com/apache/camel-k/v2` — affected >=2.9.0 <2.9.2
- Go: `github.com/apache/camel-k/v2` — affected >=2.10.0 <2.10.1

## Details
(Externally Controlled Reference to a Resource in Another Sphere), (Authorization Bypass Through User-Controlled Key) vulnerability in Apache Camel K. Authorized users in a Kubernetes namespace can create a Build resource, controlling the Pod generation in a namespace of their choice, including the operator namespace.

This issue affects Apache Camel K: from 2.0.0 before 2.8.1, from 2.9.0 before 2.9.2, from 2.10.0 before 2.10.1.

Users are recommended to upgrade to version 2.10.1 (or 2.8.1 or 2.9.2), which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45760
- https://github.com/apache/camel-k/pull/6626
- https://github.com/apache/camel-k/pull/6627
- https://github.com/apache/camel-k/pull/6629
- https://github.com/apache/camel-k/commit/1271df076f3123f5e4ec58e066e284236b1a8fb5
- https://github.com/apache/camel-k/commit/1efa3982f4dbce0ae1f896f4003a16cae6d81ba2
- https://github.com/apache/camel-k/commit/35dd387f58464608ab4764f67bde786cf09bc39d
- https://camel.apache.org/security/CVE-2026-45760.html
- https://github.com/apache/camel-k
- http://www.openwall.com/lists/oss-security/2026/05/21/8
