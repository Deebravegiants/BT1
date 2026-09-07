# [H] Undertow's url-encoded request path information can be broken on ajp-listener

## Summary
Severity: High
Advisory: GHSA-9442-gm4v-r222
CVE: CVE-2024-6162
CWE: CWE-400, CWE-488
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-9442-gm4v-r222
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.14.Final
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.33.Final

## Details
A vulnerability was found in Undertow, where URL-encoded request paths can be mishandled during concurrent requests on the AJP listener. This issue arises because the same buffer is used to decode the paths for multiple requests simultaneously, leading to incorrect path information being processed. As a result, the server may attempt to access the wrong path, causing errors such as "404 Not Found" or other application failures. This flaw can potentially lead to a denial of service, as legitimate resources become inaccessible due to the path mix-up.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6162
- https://github.com/undertow-io/undertow/pull/1612
- https://github.com/undertow-io/undertow/commit/90f202ada89b6d9883beed0f1fe10c99d470d9a8
- https://github.com/undertow-io/undertow/commit/a28ac53076e2fa532266d25e0c0b1a01d0e9d2cf
- https://access.redhat.com/errata/RHSA-2024:1194
- https://access.redhat.com/errata/RHSA-2024:4386
- https://access.redhat.com/errata/RHSA-2024:4884
- https://access.redhat.com/security/cve/CVE-2024-6162
- https://bugzilla.redhat.com/show_bug.cgi?id=2293069
- https://github.com/undertow-io/undertow
- https://github.com/undertow-io/undertow/releases/tag/2.2.33.Final
- https://github.com/undertow-io/undertow/releases/tag/2.3.14.Final
- https://issues.redhat.com/browse/JBEAP-26268
- https://issues.redhat.com/browse/UNDERTOW-2334
- https://security.netapp.com/advisory/ntap-20241129-0009
