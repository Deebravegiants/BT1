# [C] Eclipse Jersey has a Race Condition

## Summary
Severity: Critical
Advisory: GHSA-7p63-w6x9-6gr7
CVE: CVE-2025-12383
CWE: CWE-296, CWE-362
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-11-18
Source: https://github.com/advisories/GHSA-7p63-w6x9-6gr7
Type: github-advisory

## Affected
- Maven: `org.glassfish.jersey.core:jersey-client` — affected >=2.45 <2.46
- Maven: `org.glassfish.jersey.core:jersey-client` — affected >=3.0.16 <3.0.17
- Maven: `org.glassfish.jersey.core:jersey-client` — affected >=3.1.9 <3.1.10

## Details
In Eclipse Jersey versions 2.45, 3.0.16, 3.1.9 a race condition can cause ignoring of critical SSL configurations - such as mutual authentication, custom key/trust stores, and other security settings. This issue may result in SSLHandshakeException under normal circumstances, but under certain conditions, it could lead to unauthorized trust in insecure servers (see PoC)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12383
- https://github.com/eclipse-ee4j/jersey/pull/5749
- https://github.com/eclipse-ee4j/jersey/pull/5794
- https://github.com/eclipse-ee4j/jersey/commit/425bc883d8d623ef8d3c448fafd36729f7741bcb
- https://github.com/eclipse-ee4j/jersey/commit/b2c7ba6d388cb9722f39073d7e82aa818fec49d5
- https://github.com/dtbaum/jerseyCveCandidate
- https://github.com/eclipse-ee4j/jersey
- https://github.com/eclipse-ee4j/jersey/releases/tag/2.46
- https://github.com/eclipse-ee4j/jersey/releases/tag/3.0.17
- https://github.com/eclipse-ee4j/jersey/releases/tag/3.1.10
- https://github.com/eclipse-ee4j/jersey/releases/tag/4.0.0-M2
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/74
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/253
