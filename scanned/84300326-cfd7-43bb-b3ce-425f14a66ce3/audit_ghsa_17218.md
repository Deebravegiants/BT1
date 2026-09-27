# [H] Undertow OutOfMemory when parsing form data encoding with application/x-www-form-urlencoded

## Summary
Severity: High
Advisory: GHSA-6h4f-pj3g-q8fq
CVE: CVE-2024-3884
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-6h4f-pj3g-q8fq
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.39.Final
- Maven: `io.undertow:undertow-core` — affected >=2.4.0.Alpha1 <2.4.0.Beta1
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.21.Final

## Details
A flaw was found in Undertow that can cause remote denial of service attacks. When the server uses the FormEncodedDataDefinition.doParse(StreamSourceChannel) method to parse large form data encoding with application/x-www-form-urlencoded, the method will cause an OutOfMemory issue. This flaw allows unauthorized users to cause a remote denial of service (DoS) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3884
- https://github.com/undertow-io/undertow/pull/1894
- https://github.com/undertow-io/undertow/pull/1882
- https://github.com/undertow-io/undertow/pull/1860
- https://github.com/undertow-io/undertow/pull/1856
- https://github.com/undertow-io/undertow/commit/cb854c779b9e2368c3c274ebd7217c8e75d505be
- https://github.com/undertow-io/undertow/releases/tag/2.4.0.Beta1
- https://github.com/undertow-io/undertow/releases/tag/2.3.21.Final
- https://github.com/undertow-io/undertow/releases/tag/2.2.39.Final
- https://github.com/undertow-io/undertow
- https://bugzilla.redhat.com/show_bug.cgi?id=2275287
- https://access.redhat.com/security/cve/CVE-2024-3884
- https://access.redhat.com/errata/RHSA-2026:6012
- https://access.redhat.com/errata/RHSA-2026:6011
- https://access.redhat.com/errata/RHSA-2026:4924
- https://access.redhat.com/errata/RHSA-2026:4917
- https://access.redhat.com/errata/RHSA-2026:4916
- https://access.redhat.com/errata/RHSA-2026:4915
- https://access.redhat.com/errata/RHSA-2026:3892
- https://access.redhat.com/errata/RHSA-2026:3891
