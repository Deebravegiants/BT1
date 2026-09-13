# [H] nanobot: Path traversal via unsanitized WhatsApp document fileName enables arbitrary file write

## Summary
Severity: High
Advisory: CVE-2026-48716
Aliases: GHSA-3f63-vcp3-hvqr
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-48716
Type: osv

## Details
nanobot is a personal AI assistant. In versions 0.1.5.post3 and prior, the WhatsApp bridge in bridge/src/whatsapp.ts constructs a filesystem path using the fileName field from an incoming WhatsApp document message without sanitization. The WhatsApp bridge downloads media attachments and writes them to disk using a filename derived from the sender's message via documentMessage.fileName, which is concatenated with a prefix and its raw value is passed directly to path.join(mediaDir, outFilename). Node.js path.join resolves .. components, allowing an attacker to escape the intended media/ directory by sending a document with a crafted fileName such as ../../../.ssh/authorized_keys. Because the attacker also controls the file content (the downloaded buffer), this is a write-anywhere primitive — both path and content are attacker-controlled. A fix for this issue is planned for version 0.1.5.post4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48716.json
- https://github.com/HKUDS/nanobot/security/advisories/GHSA-3f63-vcp3-hvqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48716
