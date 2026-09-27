# [H] Undertow vulnerable to Race Condition

## Summary
Severity: High
Advisory: GHSA-9623-mqmm-5rcf
CVE: CVE-2024-7885
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-9623-mqmm-5rcf
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.36.Final
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.17.Final

## Details
A vulnerability was found in Undertow where the ProxyProtocolReadListener reuses the same StringBuilder instance across multiple requests. This issue occurs when the parseProxyProtocolV1 method processes multiple requests on the same HTTP connection. As a result, different requests may share the same StringBuilder instance, potentially leading to information leakage between requests or responses. In some cases, a value from a previous request or response may be erroneously reused, which could lead to unintended data exposure. This issue primarily results in errors and connection termination but creates a risk of data leakage in multi-request environments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7885
- https://github.com/undertow-io/undertow/commit/ce5182c37376982ef0abee34fce0d8c0aab0fab8
- https://github.com/undertow-io/undertow/commit/80c125e09068ac52ed0a9acde266ef12f8ed7ae1
- https://security.netapp.com/advisory/ntap-20241011-0004
- https://github.com/undertow-io/undertow/blob/182e4ca1543c52f438b0244c930dca3d8b6e68e3/core/src/main/java/io/undertow/server/protocol/proxy/ProxyProtocolReadListener.java
- https://github.com/undertow-io/undertow
- https://bugzilla.redhat.com/show_bug.cgi?id=2305290
- https://access.redhat.com/security/cve/CVE-2024-7885
- https://access.redhat.com/errata/RHSA-2026:0743
- https://access.redhat.com/errata/RHSA-2025:16667
- https://access.redhat.com/errata/RHSA-2024:8080
- https://access.redhat.com/errata/RHSA-2024:7736
- https://access.redhat.com/errata/RHSA-2024:7735
- https://access.redhat.com/errata/RHSA-2024:7442
- https://access.redhat.com/errata/RHSA-2024:7441
- https://access.redhat.com/errata/RHSA-2024:6883
- https://access.redhat.com/errata/RHSA-2024:6508
- https://access.redhat.com/errata/RHSA-2024:11023
