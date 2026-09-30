# [C] Apache Fory Java SDK Has Deserialization of Untrusted Data in the Java replace-resolve path

## Summary
Severity: Critical
Advisory: GHSA-8f39-v287-78jf
CVE: CVE-2026-50076
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-8f39-v287-78jf
Type: github-advisory

## Affected
- Maven: `org.apache.fory:fory-core` — affected >=0 <1.1.0

## Details
Deserialization of Untrusted Data in the Java replace-resolve path in Apache Fory fory-core Java SDK before 1.1.0 on Java/JVM platforms allows a remote attacker to bypass class registration, TypeChecker, and DisallowedList checks and invoke classpath-present readResolve/readExternal hooks via crafted Fory serialized data.

Users are recommended to upgrade to version 1.1.0 or later, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50076
- https://fory.apache.org/security
- https://github.com/apache/fory
- http://www.openwall.com/lists/oss-security/2026/06/04/4
