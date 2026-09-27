# [M] Debezium database connector has a script injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hvw5-3mgw-7rcf
CVE: CVE-2023-1419
CWE: CWE-233
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-17
Source: https://github.com/advisories/GHSA-hvw5-3mgw-7rcf
Type: github-advisory

## Affected
- Maven: `io.debezium:debezium-connector-mysql` — affected >=0 <2.3.0.Alpha1
- Maven: `io.debezium:debezium-connector-sqlserver` — affected >=0 <2.3.0.Alpha1
- Maven: `io.debezium:debezium-core` — affected >=0 <2.3.0.Alpha1

## Details
A script injection vulnerability was found in the Debezium database connector, where it does not properly sanitize some parameters. This flaw allows an attacker to send a malicious request to inject a parameter that may allow the viewing of unauthorized data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1419
- https://github.com/debezium/debezium/commit/58ef4f0b98428cc795c2844eaa6e1762e8248227
- https://access.redhat.com/security/cve/CVE-2023-1419
- https://bugzilla.redhat.com/show_bug.cgi?id=2178722
- https://github.com/debezium/debezium
