# [H] Graylog Allows Session Takeover via Insufficient HTML Sanitization

## Summary
Severity: High
Advisory: GHSA-76vf-mpmx-777j
CVE: CVE-2025-46827
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-07
Source: https://github.com/advisories/GHSA-76vf-mpmx-777j
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=0 <6.0.14
- Maven: `org.graylog2:graylog2-server` — affected >=6.1.0 <6.1.10

## Details
### Impact
It is possible to obtain user session cookies by submitting an HTML form as part of an Event Definition Remediation Step field. 
For this attack to succeed, the attacker needs a user account with permissions to create event definitions, while the user must have permissions to view alerts. Additionally, an active Input must be present on the Graylog server that is capable of receiving form data (e.g. a HTTP input, TCP raw or syslog etc).

### Patches

### Workarounds
None, as long as the relatively rare prerequisites are met.

Analysis provided by Fabian Yamaguchi - Whirly Labs (Pty) Ltd

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-76vf-mpmx-777j
- https://nvd.nist.gov/vuln/detail/CVE-2025-46827
- https://github.com/Graylog2/graylog2-server
