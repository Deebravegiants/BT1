# [H] CVE-2026-17613

## Summary
Severity: High
Advisory: CVE-2026-17613
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-17613
Type: osv

## Details
Penpot’s ::import-binfile RPC command lacks authorization on the optional file-id parameter, allowing any authenticated user to overwrite any files on the target server and subscribe to WebSocket events, enabling full data exfiltration and data poisoning.

## References
- https://github.com/penpot/penpot/releases/tag/2.17.0
- https://penpot.app/
- https://vokecyber.com/research/cve-2026-17613-penpot-cross-team-file-takeover
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17613.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17613
- https://vokecyber.com/blog/cve-2026-17613-penpot-cross-team-file-takeover
