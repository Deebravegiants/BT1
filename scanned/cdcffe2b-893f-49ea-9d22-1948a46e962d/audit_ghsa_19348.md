# [H] Tornado vulnerable to excessive logging caused by malformed multipart form data

## Summary
Severity: High
Advisory: GHSA-7cx3-6m66-7c5m
CVE: CVE-2025-47287
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-16
Source: https://github.com/advisories/GHSA-7cx3-6m66-7c5m
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5

## Details
### Summary

When Tornado's ``multipart/form-data`` parser encounters certain errors, it logs a warning but continues trying to parse the remainder of the data. This allows remote attackers to generate an extremely high volume of logs, constituting a DoS attack. This DoS is compounded by the fact that the logging subsystem is synchronous.

### Affected versions

All versions of Tornado prior to 6.5 are affected. The vulnerable parser is enabled by default.

### Solution

Upgrade to Tornado version 6.5. In the meantime, risk can be mitigated by blocking `Content-Type: multipart/form-data` in a proxy.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-7cx3-6m66-7c5m
- https://nvd.nist.gov/vuln/detail/CVE-2025-47287
- https://github.com/tornadoweb/tornado/commit/b39b892bf78fe8fea01dd45199aa88307e7162f3
- https://github.com/tornadoweb/tornado
- https://lists.debian.org/debian-lts-announce/2025/05/msg00038.html
