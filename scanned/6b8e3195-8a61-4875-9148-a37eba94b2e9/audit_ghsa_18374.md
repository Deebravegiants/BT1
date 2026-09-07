# [H] Undertow MadeYouReset HTTP/2 DDoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-95h4-w6j8-2rp8
CVE: CVE-2025-9784
CWE: CWE-404, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-02
Source: https://github.com/advisories/GHSA-95h4-w6j8-2rp8
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.38.Final
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.20.Final

## Details
A flaw was found in Undertow where malformed client requests can trigger server-side stream resets without triggering abuse counters. This issue, referred to as the "MadeYouReset" attack, allows malicious clients to induce excessive server workload by repeatedly causing server-side stream aborts. While not a protocol bug, this highlights a common implementation weakness that can be exploited to cause a denial of service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9784
- https://github.com/undertow-io/undertow/pull/1805
- https://github.com/undertow-io/undertow/pull/1804
- https://github.com/undertow-io/undertow/pull/1803
- https://github.com/undertow-io/undertow/pull/1802
- https://github.com/undertow-io/undertow/pull/1778
- https://www.kb.cert.org/vuls/id/767506
- https://kb.cert.org/vuls/id/767506
- https://issues.redhat.com/browse/UNDERTOW-2598
- https://github.com/undertow-io/undertow/releases/tag/2.2.38.Final
- https://github.com/undertow-io/undertow
- https://bugzilla.redhat.com/show_bug.cgi?id=2392306
- https://access.redhat.com/security/cve/CVE-2025-9784
- https://access.redhat.com/errata/RHSA-2026:4924
- https://access.redhat.com/errata/RHSA-2026:4917
- https://access.redhat.com/errata/RHSA-2026:4916
- https://access.redhat.com/errata/RHSA-2026:4915
- https://access.redhat.com/errata/RHSA-2026:3892
- https://access.redhat.com/errata/RHSA-2026:3891
- https://access.redhat.com/errata/RHSA-2026:3889
