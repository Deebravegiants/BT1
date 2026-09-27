# [M] FreeSWITCH: Pre-authentication `userVariables` injection in `mod_verto`

## Summary
Severity: Medium
Advisory: CVE-2026-49848
Aliases: GHSA-j38x-xm7f-9p2f
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49848
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.11.1, mod_verto's check_auth userauth branch wrote request-supplied userVariables into the connection state before comparing the supplied password. The writes are append-only and the connection is not closed on a failed compare, so values declared on bad-password attempts persisted on the same WebSocket and carried into a subsequent successful login on that connection. This issue has been patched in version 1.11.1.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49848.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-j38x-xm7f-9p2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-49848
