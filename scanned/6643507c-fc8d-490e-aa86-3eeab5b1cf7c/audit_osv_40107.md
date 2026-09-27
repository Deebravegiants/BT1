# [M] FreeSWITCH: Pre-authentication session eviction via attacker-chosen `sessid` in `mod_verto`

## Summary
Severity: Medium
Advisory: CVE-2026-49843
Aliases: GHSA-9457-fxr9-x78m
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49843
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.11.1, mod_verto's JSON-RPC handler bound the connection to the client-supplied sessid on the first frame, before the authentication gate. Binding inserts the connection into the global session hash and, on a key collision, drops the prior occupant of that slot — sending it a verto.punt, detaching its calls, and closing its socket. An unauthenticated network attacker who knows a target session UUID could therefore evict the legitimate client. This issue has been patched in version 1.11.1.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49843.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-9457-fxr9-x78m
- https://nvd.nist.gov/vuln/detail/CVE-2026-49843
