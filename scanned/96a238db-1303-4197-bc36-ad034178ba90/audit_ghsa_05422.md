# [H] Undertow Servlets Vulnerable to Remote DoS via OutOfMemoryError when Passed Large Parameter Names

## Summary
Severity: High
Advisory: GHSA-33hj-rcmx-86mv
CVE: CVE-2024-4027
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-30
Source: https://github.com/advisories/GHSA-33hj-rcmx-86mv
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.39.Final
- Maven: `io.undertow:undertow-core` — affected >=2.4.0.Alpha1 <2.4.0.Beta1
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.21.Final

## Details
A flaw was found in Undertow. Servlets using a method that calls HttpServletRequestImpl.getParameterNames() can cause an OutOfMemoryError when the client sends a request with large parameter names. This issue can be exploited by an unauthorized user to cause a remote denial-of-service (DoS) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4027
- https://github.com/undertow-io/undertow/pull/1860
- https://github.com/undertow-io/undertow/pull/1882
- https://github.com/undertow-io/undertow/pull/1894
- https://github.com/undertow-io/undertow/commit/6b7c18481ce65ae4012d92fe2b7f17a21ef4d70b
- https://github.com/undertow-io/undertow/commit/8318dd36fdc2c9842baf10c5f1bfbb3bc23f75e7
- https://github.com/undertow-io/undertow/commit/cb854c779b9e2368c3c274ebd7217c8e75d505be
- https://github.com/undertow-io/undertow/commit/fb14baa51b611a4a9f755f1d8b07d6e12eac68e3
- https://access.redhat.com/security/cve/CVE-2024-4027
- https://bugzilla.redhat.com/show_bug.cgi?id=2276410
- https://github.com/undertow-io/undertow
- https://github.com/undertow-io/undertow/releases/tag/2.2.39.Final
- https://github.com/undertow-io/undertow/releases/tag/2.3.21.Final
- https://github.com/undertow-io/undertow/releases/tag/2.4.0.Beta1
- https://issues.redhat.com/browse/UNDERTOW-2377
