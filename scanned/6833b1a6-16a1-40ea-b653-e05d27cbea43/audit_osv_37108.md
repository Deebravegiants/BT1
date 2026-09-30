# [M] Textream Vulnerable to Uncontrolled Resource Consumption (Denial of Service)

## Summary
Severity: Medium
Advisory: CVE-2026-28412
Aliases: GHSA-qr5p-7x47-qxh9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2026-28412
Type: osv

## Details
Textream is a free macOS teleprompter app. Prior to version 1.5.1, the `DirectorServer` WebSocket server imposes no limit on concurrent connections. Combined with a broadcast timer that sends state to all connected clients every 100 ms, an attacker can exhaust CPU and memory by flooding the server with connections, causing the Textream application to freeze and crash during a live session. Version 1.5.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28412.json
- https://github.com/f/textream/security/advisories/GHSA-qr5p-7x47-qxh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-28412
- https://github.com/f/textream/commit/3524fa96f98ba17025b48ce9e19d49d859fc2ec1
