# [H] Graylog Allows Stored Cross-Site Scripting via Files Plugin and API Browser

## Summary
Severity: High
Advisory: GHSA-q9q2-3ppx-mwqf
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-05-07
Source: https://github.com/advisories/GHSA-q9q2-3ppx-mwqf
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=0 <6.2.0

## Details
### Impact
Two minor vulnerabilities were identified in the Graylog2 enterprise server, which can be combined to carry out a stored cross-site scripting attack.
An attacker with the permission `FILES_CREATE` can exploit these vulnerabilities to upload arbitrary Javascript code to the Graylog2 server, which - upon requesting of the file by a user of the API browser - results in the execution of this Javascript code in the context of the Graylog frontend application. 
This enables the attacker to carry out authenticated API requests with the permissions of the logged-in user, thereby taking over the user session.

### Patches
The generic API has been removed in 6.2.0 rendering the attack vector unreachable and additional escaping has been added.

Analysis provided by Fabian Yamaguchi - Whirly Labs (Pty) Ltd

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-q9q2-3ppx-mwqf
- https://github.com/Graylog2/graylog2-server
