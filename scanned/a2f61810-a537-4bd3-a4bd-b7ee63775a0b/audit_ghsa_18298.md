# [M] Apache Fory Deserialization of Untrusted Data vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5hmf-8wx5-4qq3
CVE: CVE-2025-59328
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-5hmf-8wx5-4qq3
Type: github-advisory

## Affected
- Maven: `org.apache.fory:fory-core` — affected >=0 <0.12.2

## Details
A vulnerability in Apache Fory allows a remote attacker to cause a Denial of Service (DoS). The issue stems from the insecure deserialization of untrusted data. An attacker can supply a large, specially crafted data payload that, when processed, consumes an excessive amount of CPU resources during the deserialization process. This leads to CPU exhaustion, rendering the application or system using the Apache Fory library unresponsive and unavailable to legitimate users.

Users of Apache Fory are strongly advised to upgrade to version 0.12.2 or later to mitigate this vulnerability. Developers of libraries and applications that depend on Apache Fory should update their dependency requirements to Apache Fory 0.12.2 or later and release new versions of their software.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59328
- https://github.com/apache/fory/pull/2578
- https://github.com/apache/fory/commit/c3b4d3fe389e38495aeb8301d75da1ab658f0c6e
- https://fory.apache.org/security
- https://github.com/apache/fory
- https://github.com/apache/fory/releases/tag/v0.12.2
- http://www.openwall.com/lists/oss-security/2025/09/15/1
