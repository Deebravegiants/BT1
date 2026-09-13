# [C] Nanobot Unauthenticated WhatsApp Session Hijack via WebSocket Bridge

## Summary
Severity: Critical
Advisory: CVE-2026-2577
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-02-16
Source: https://osv.dev/vulnerability/CVE-2026-2577
Type: osv

## Details
The WhatsApp bridge component in Nanobot binds the WebSocket server to all network interfaces (0.0.0.0) on port 3001 by default and does not require authentication for incoming connections. An unauthenticated remote attacker with network access to the bridge can connect to the WebSocket server to hijack the WhatsApp session. This allows the attacker to send messages on behalf of the user, intercept all incoming messages and media in real-time, and capture authentication QR codes.

## References
- https://github.com/HKUDS/nanobot/releases/tag/v0.1.3.post7
- https://www.tenable.com/security/research/tra-2026-09
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2577.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2577
