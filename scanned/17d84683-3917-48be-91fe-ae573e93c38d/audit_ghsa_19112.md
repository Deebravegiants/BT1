# [H] Quarkus REST Endpoint Request Parameter Leakage Due to Shared Instance

## Summary
Severity: High
Advisory: GHSA-phg3-gv66-q38x
CVE: CVE-2025-1247
CWE: CWE-488
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-02-13
Source: https://github.com/advisories/GHSA-phg3-gv66-q38x
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-rest` — affected >=3.16.0.CR1 <3.18.2
- Maven: `io.quarkus:quarkus-rest-deployment` — affected >=3.16.0.CR1 <3.18.2
- Maven: `io.quarkus:quarkus-rest` — affected >=3.9.0.CR1 <3.15.3.1
- Maven: `io.quarkus:quarkus-rest-deployment` — affected >=3.9.0.CR1 <3.15.3.1
- Maven: `io.quarkus:quarkus-rest` — affected >=0 <3.8.6.1
- Maven: `io.quarkus:quarkus-rest-deployment` — affected >=0 <3.8.6.1

## Details
A flaw was found in Quarkus REST that allows request parameters to leak between concurrent requests if endpoints use field injection without a CDI scope. This vulnerability allows attackers to manipulate request data, impersonate users, or access sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1247
- https://github.com/quarkusio/quarkus/issues/45789
- https://github.com/quarkusio/quarkus/commit/02ff9ed45c3928edf2a0f8b906543606fed7cd53
- https://github.com/quarkusio/quarkus/commit/d8df15cec17dc5d085efc372d77cbef1341ae071
- https://github.com/quarkusio/quarkus/commit/f42166ee7041ed09b7183d5dbf3ece2439b16676
- https://access.redhat.com/errata/RHSA-2025:1884
- https://access.redhat.com/errata/RHSA-2025:1885
- https://access.redhat.com/errata/RHSA-2025:2067
- https://access.redhat.com/security/cve/CVE-2025-1247
- https://bugzilla.redhat.com/show_bug.cgi?id=2345172
- https://github.com/quarkusio/quarkus
- https://quarkus.io/blog/cve-fixes-feb-2025
