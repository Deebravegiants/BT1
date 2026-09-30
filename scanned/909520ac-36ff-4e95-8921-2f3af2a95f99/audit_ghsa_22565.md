# [M] Ignite Realtime Openfire directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-59h8-h34r-q9cv
CVE: CVE-2019-18393
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-59h8-h34r-q9cv
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.openfire:parent` — affected >=0 <4.5.0-beta

## Details
PluginServlet.java in Ignite Realtime Openfire through 4.4.2 does not ensure that retrieved files are located under the Openfire home directory, aka a directory traversal vulnerability. Version 4.5.0-beta contains a fix for the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18393
- https://github.com/igniterealtime/Openfire/pull/1498
- https://github.com/igniterealtime/Openfire/commit/cb900749d4e836b32cc6e2cc41cda17f252b977d
- https://swarm.ptsecurity.com/openfire-admin-console
