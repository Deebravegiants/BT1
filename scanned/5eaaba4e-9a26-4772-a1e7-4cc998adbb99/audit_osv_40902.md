# [H] Chainlit < 2.10.1 Session Hijacking via WebSocket Session Restoration

## Summary
Severity: High
Advisory: CVE-2026-56104
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56104
Type: osv

## Details
Chainlit before 2.10.1 contains a session hijacking vulnerability that allows unauthenticated attackers to restore and inherit authenticated user sessions by presenting a valid sessionId during WebSocket session restoration without ownership verification. Attackers can exploit the restore_existing_session path to assume a victim's permissions and roles, enabling unauthorized invocation of tools and access to data restricted to the authenticated victim.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56104.json
- https://github.com/Chainlit/chainlit/releases/tag/2.10.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-56104
- https://www.vulncheck.com/advisories/chainlit-session-hijacking-via-websocket-session-restoration
- https://github.com/Chainlit/chainlit/pull/2857
- https://github.com/Chainlit/chainlit/commit/5effb664f1e0af4a4f0a42fe63ea979676039a7f
- https://github.com/Chainlit/chainlit
