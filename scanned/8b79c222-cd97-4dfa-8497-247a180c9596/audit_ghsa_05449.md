# [M] Hibernate Reactive Vulnerable to DoS via Connection Pool Exhaustion

## Summary
Severity: Medium
Advisory: GHSA-frpp-8pwq-hjrx
CVE: CVE-2025-14969
CWE: CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-frpp-8pwq-hjrx
Type: github-advisory

## Affected
- Maven: `org.hibernate.reactive:hibernate-reactive-core` — affected >=0 <4.2.1

## Details
A flaw was found in Hibernate Reactive. When an HTTP endpoint is exposed to perform database operations, a remote client can prematurely close the HTTP connection. This action may lead to leaking connections from the database connection pool, potentially causing a Denial of Service (DoS) by exhausting available database connections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14969
- https://github.com/hibernate/hibernate-reactive/commit/cd7f104e10de918004707ca0e26e3840976f780a
- https://access.redhat.com/errata/RHSA-2026:1965
- https://access.redhat.com/security/cve/CVE-2025-14969
- https://bugzilla.redhat.com/show_bug.cgi?id=2423822
- https://github.com/hibernate/hibernate-reactive
