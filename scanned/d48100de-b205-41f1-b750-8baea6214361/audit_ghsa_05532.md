# [C] React Router has Path Traversal in File Session Storage

## Summary
Severity: Critical
Advisory: GHSA-9583-h5hc-x8cw
CVE: CVE-2025-61686
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-9583-h5hc-x8cw
Type: github-advisory

## Affected
- npm: `@react-router/node` — affected >=7.0.0 <7.9.4
- npm: `@remix-run/node` — affected >=0 <2.17.2
- npm: `@remix-run/deno` — affected >=0 <2.17.2

## Details
If applications use `createFileSessionStorage()` from `@react-router/node` (or `@remix-run/node`/`@remix-run/deno` in Remix v2) with an [**unsigned cookie**](https://reactrouter.com/explanation/sessions-and-cookies#signing-cookies), it is possible for an attacker to cause the session to try to read/write from a location outside the specified session file directory. The success of the attack would depend on the permissions of the web server process to access those files. 

Read files cannot be returned directly to the attacker.  Session file reads would only succeed if the file matched the expected session file format. If the file matched the session file format, the data would be populated into the server side session but not directly returned to the attacker unless the application logic returned specific session information.

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-9583-h5hc-x8cw
- https://nvd.nist.gov/vuln/detail/CVE-2025-61686
- https://github.com/remix-run/react-router
