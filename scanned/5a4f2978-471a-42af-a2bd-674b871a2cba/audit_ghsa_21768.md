# [H] Pivotal Concourse SQL Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-4fqx-74rv-638w
CVE: CVE-2019-3792
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-4fqx-74rv-638w
Type: github-advisory

## Affected
- Go: `github.com/concourse/concourse` — affected >=0 <5.0.1

## Details
Pivotal Concourse version 5.0.0, contains an API that is vulnerable to SQL injection. An Concourse resource can craft a version identifier that can carry a SQL injection payload to the Concourse server, allowing the attacker to read privileged data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3792
- https://github.com/concourse/concourse/commit/dc3d15ab6c3a69890c9985f9c875d4c2949be727
- https://github.com/concourse/concourse/blob/master/release-notes/v5.0.1.md#v501-note-1
- https://pivotal.io/security/cve-2019-3792
