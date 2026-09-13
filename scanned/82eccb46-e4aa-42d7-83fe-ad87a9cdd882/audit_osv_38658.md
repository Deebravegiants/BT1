# [H] STIG Manager has reflected XSS vulnerability in the Web App

## Summary
Severity: High
Advisory: CVE-2026-41200
Aliases: GHSA-wg33-j3rv-jq72
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-41200
Type: osv

## Details
STIG Manager is an API and web client for managing  Security Technical Implementation Guides (STIG) assessments of Information Systems. Versions 1.5.10 through 1.6.7 have a reflected Cross-Site Scripting (XSS) vulnerability in the OIDC authentication error handling code in `src/init.js` and `public/reauth.html`. During the OIDC redirect flow, the `error` and `error_description` query parameters returned by the OIDC provider are written directly to the DOM via `innerHTML` without HTML escaping. An attacker who can craft a malicious redirect URL and convince a user to follow it can execute arbitrary JavaScript in the application's origin context. The vulnerability is most severe when the targeted user has an active STIG Manager session running in another browser tab — injected code executes in the same origin and can communicate with the SharedWorker managing the active access token, enabling authenticated API requests on behalf of the victim including reading and modifying collection data. The vulnerability is patched in version 1.6.8. There is no workaround short of upgrading. Deployments behind a web application firewall that filters reflected XSS payloads in query parameters may have partial mitigation, but this is not a substitute for patching.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41200.json
- https://github.com/NUWCDIVNPT/stig-manager/security/advisories/GHSA-wg33-j3rv-jq72
- https://nvd.nist.gov/vuln/detail/CVE-2026-41200
