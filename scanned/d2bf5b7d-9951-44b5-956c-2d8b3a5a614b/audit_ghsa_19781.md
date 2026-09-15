# [H] SmallRye Fault Tolerance out-of-memory (OOM) issue

## Summary
Severity: High
Advisory: GHSA-gfh6-3pqw-x2j4
CVE: CVE-2025-2240
CWE: CWE-1325
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-gfh6-3pqw-x2j4
Type: github-advisory

## Affected
- Maven: `io.smallrye:smallrye-fault-tolerance-core` — affected >=6.3.0 <6.4.2
- Maven: `io.smallrye:smallrye-fault-tolerance-core` — affected >=6.5.0 <6.9.0

## Details
A flaw was found in Smallrye, where smallrye-fault-tolerance is vulnerable to an out-of-memory (OOM) issue. This vulnerability is externally triggered when calling the metrics URI. Every call creates a new object within meterMap and may lead to a denial of service (DoS) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2240
- https://github.com/smallrye/smallrye-fault-tolerance/pull/985
- https://github.com/smallrye/smallrye-fault-tolerance/pull/985/files#diff-88c4a089e0cb88e4bdf285490e2617c29b9979a778e33957e4448260e286b91aR299
- https://github.com/smallrye/smallrye-fault-tolerance/commit/e8bcad3d5e8bbac0a3219bd5c13661adf6ed6bbb
- https://access.redhat.com/errata/RHSA-2025:3376
- https://access.redhat.com/errata/RHSA-2025:3541
- https://access.redhat.com/errata/RHSA-2025:3543
- https://access.redhat.com/security/cve/CVE-2025-2240
- https://bugzilla.redhat.com/show_bug.cgi?id=2351452
- https://github.com/smallrye/smallrye-fault-tolerance
- https://smallrye.io/blog/fault-tolerance-6-9-0
