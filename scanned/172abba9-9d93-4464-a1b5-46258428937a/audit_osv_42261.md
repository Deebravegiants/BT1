# [H] OpenRemote before 1.26.2 Authentication Bypass via Console Registration

## Summary
Severity: High
Advisory: CVE-2026-66013
Aliases: GHSA-gpfc-h59v-63cv
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-66013
Type: osv

## Details
OpenRemote before 1.26.2 contains an authentication bypass vulnerability in the console registration API that allows unauthenticated attackers to update existing console assets by supplying a known asset identifier. Attackers can overwrite push notification tokens and console metadata without authentication or ownership validation, redirecting notifications or denying delivery to legitimate consoles.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66013.json
- https://github.com/openremote/openremote/security/advisories/GHSA-gpfc-h59v-63cv
- https://nvd.nist.gov/vuln/detail/CVE-2026-66013
- https://www.vulncheck.com/advisories/openremote-before-authentication-bypass-via-console-registration
