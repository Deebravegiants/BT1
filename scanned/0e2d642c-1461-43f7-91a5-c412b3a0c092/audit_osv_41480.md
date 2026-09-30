# [M] Grav before 2.0.4 Information Disclosure via __GRAV_CONFIG__

## Summary
Severity: Medium
Advisory: CVE-2026-61454
Aliases: GHSA-pfjq-chp8-3vgh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/CVE-2026-61454
Type: osv

## Details
The Grav Admin2 plugin (getgrav/grav-plugin-admin2) before 2.0.4 embeds a global JavaScript variable window.__GRAV_CONFIG__ in the Admin2 SPA bootstrap page at /grav/admin (and its subroutes). This object is returned in every unauthenticated response and discloses the server URL, API prefix, admin base path, runtime environment type, and exact Grav and Admin2 version numbers, allowing an unauthenticated attacker to fingerprint the deployment and select version-specific exploits without reconnaissance.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61454.json
- https://github.com/getgrav/grav/security/advisories/GHSA-pfjq-chp8-3vgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-61454
- https://www.vulncheck.com/advisories/grav-before-information-disclosure-via-grav-config
