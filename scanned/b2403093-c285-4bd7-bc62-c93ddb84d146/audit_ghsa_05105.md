# [H] Sync-in Server: SSRF protection bypass via IPv4-mapped IPv6 addresses in regExpPrivateIP

## Summary
Severity: High
Advisory: GHSA-q4x5-8cj6-52wg
CVE: CVE-2026-47684
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-q4x5-8cj6-52wg
Type: github-advisory

## Affected
- npm: `@sync-in/server` — affected >=0 <2.3.0

## Details
Summary:
The private IP blocklist regex used in the URL download feature does not match IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1), allowing SSRF protection to be bypassed on dual-stack systems.

Affected components

backend/src/applications/files/services/files-manager.service.ts – downloadFromUrl() checks regExpPrivateIP against request.socket.remoteAddress.
backend/src/applications/files/utils/url-file.ts – regExpPrivateIP does not include ::ffff:<ipv4> variants.

Details:
The regExpPrivateIP regex in backend/src/applications/files/utils/url-file.ts correctly blocks standard IPv4 private ranges but does not include ::ffff: prefixed variants. On dual-stack systems, Node.js can report a socket's remoteAddress in IPv4-mapped IPv6 form, meaning the check in FilesManager.downloadFromUrl() can be bypassed entirely.

PoC:
[poc.pdf](https://github.com/user-attachments/files/26990874/poc.pdf)




Proof:
<img width="1080" height="842" alt="1000226655" src="https://github.com/user-attachments/assets/797cea83-0a08-4a16-a91b-31c51068d473" />





Impact:
An attacker can supply a crafted URL pointing to an internal address that gets reported as ::ffff:127.0.0.1 or ::ffff:10.x.x.x, causing the server to fetch internal resources that should be blocked. Any user with access to the file download feature is a potential attacker.

## References
- https://github.com/Sync-in/server/security/advisories/GHSA-q4x5-8cj6-52wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47684
- https://github.com/Sync-in/server
- https://github.com/Sync-in/server/releases/tag/v2.3.0
