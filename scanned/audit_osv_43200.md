# [M] FreeRDP before 3.30.0 RDSTLS Server Authentication Bypass via PDU-type Confusion

## Summary
Severity: Medium
Advisory: CVE-2026-72746
Aliases: CVE-2026-73241, GHSA-rqgv-grx4-xm6x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72746
Type: osv

## Details
FreeRDP before 3.30.0 contains a server-side authentication bypass in the RDSTLS handshake. When a server is configured with RdstlsSecurity = TRUE, the handshake dispatches inbound PDUs based solely on the attacker-supplied wire pduType without verifying that the received PDU is the one required at the current step. Because the rdpRdstls object is calloc-zeroed, its resultCode defaults to 0 (RDSTLS_RESULT_SUCCESS). An unauthenticated remote client can send a Capabilities PDU instead of the required Authentication Request PDU; rdstls_process_capabilities() returns success without ever setting resultCode, so the server responds with an AUTHRSP carrying resultCode SUCCESS and treats the session as authenticated without evaluating any password, redirection GUID, or auto-reconnect cookie. This affects the released FreeRDP 3.x series (e.g., 3.27.1) and master HEAD; at the time of the advisory no patched version was available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72746.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-rqgv-grx4-xm6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-72746
- https://www.vulncheck.com/advisories/freerdp-before-rdstls-server-authentication-bypass-via-pdu-type-confusion
- https://github.com/FreeRDP/FreeRDP/commit/b05a9510787c83c87ffc5fa8d7cc9f06ed971695
