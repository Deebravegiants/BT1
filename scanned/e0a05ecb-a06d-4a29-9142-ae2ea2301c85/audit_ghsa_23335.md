# [C] Ignite Realtime Openfire vulnerable to Server Side Request Forgery 

## Summary
Severity: Critical
Advisory: GHSA-mfjw-x4q4-69p9
CVE: CVE-2019-18394
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mfjw-x4q4-69p9
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.openfire:parent` — affected >=0 <4.5.0-beta

## Details
A Server Side Request Forgery (SSRF) vulnerability in FaviconServlet.java in Ignite Realtime Openfire through 4.4.2 allows attackers to send arbitrary HTTP GET requests. The issue is fixed in version 4.5.0-beta.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18394
- https://github.com/igniterealtime/Openfire/pull/1497
- https://github.com/igniterealtime/Openfire/commit/c2ccb38250910587498597955d0bbee8b58e46df
- https://github.com/igniterealtime/Openfire
- https://swarm.ptsecurity.com/openfire-admin-console
