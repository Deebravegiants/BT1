# [M] Quarkus Cache Runtime exposes sensitive information to an unauthorized actor

## Summary
Severity: Medium
Advisory: GHSA-xfv5-jqgp-vqhj
CVE: CVE-2023-6393
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-06
Source: https://github.com/advisories/GHSA-xfv5-jqgp-vqhj
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-cache` — affected >=3.3.0.CR1 <3.5.2
- Maven: `io.quarkus:quarkus-cache` — affected >=3.2.0.CR1 <3.2.9.Final

## Details
A flaw was found in the Quarkus Cache Runtime. When request processing utilizes a Uni cached using @CacheResult and the cached Uni reuses the initial "completion" context, the processing switches to the cached Uni instead of the request context. This is a problem if the cached Uni context contains sensitive information, and could allow a malicious user to benefit from a POST request returning the response that is meant for another user, gaining access to sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6393
- https://github.com/quarkusio/quarkus/issues/37078
- https://github.com/quarkusio/quarkus/pull/37077
- https://github.com/quarkusio/quarkus/commit/d9ace85caec2d8497b1a2c48b8d52bb163f04adf
- https://access.redhat.com/errata/RHSA-2023:7700
- https://access.redhat.com/security/cve/CVE-2023-6393
- https://bugzilla.redhat.com/show_bug.cgi?id=2253113
- https://github.com/quarkusio/quarkus
