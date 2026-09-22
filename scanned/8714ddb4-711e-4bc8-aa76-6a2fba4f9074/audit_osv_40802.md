# [C] Browser Server WebSocket origin validation bypass via unanchored regex (patch bypass of CVE-2026-40289 / GHSA-8x8f-54wf-vv92)

## Summary
Severity: Critical
Advisory: CVE-2026-55536
Aliases: GHSA-6g6r-q6gw-w8fg, PYSEC-2026-3886
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-55536
Type: osv

## Details
PraisonAI is a multi-agent teams system. Prior to praisonai 4.6.58, Browser Server _handle_connection() checks Chrome extension origins with re.match() and the unanchored expression chrome-extension://[a-z0-9]{32}. Extra trailing characters pass before websocket.accept(), allowing start_session commands and unauthorized browser automation. This issue is fixed in version 4.6.58.

## References
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55536.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-6g6r-q6gw-w8fg
- https://nvd.nist.gov/vuln/detail/CVE-2026-55536
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
