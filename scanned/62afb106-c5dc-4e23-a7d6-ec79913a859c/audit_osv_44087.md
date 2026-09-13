# [C] NanoClaw Host/Container Filesystem Boundary Vulnerability via Outbound Attachment Handling

## Summary
Severity: Critical
Advisory: CVE-2026-7875
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-7875
Type: osv

## Details
NanoClaw version 1.2.0 and prior contains a host/container filesystem boundary vulnerability in outbound attachment handling and outbox cleanup that allows a compromised or prompt-injected container to read files outside the intended outbox directory by supplying crafted messages_out.id and content.files values or creating symlinked outbox files. Attackers can exploit this vulnerability to trigger host-side reads of arbitrary files and in some cases achieve recursive deletion of paths outside the intended cleanup target.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7875.json
- https://github.com/qwibitai/nanoclaw/releases/tag/v1.2.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-7875
- https://github.com/qwibitai/nanoclaw/pull/2001
- https://github.com/qwibitai/nanoclaw/commit/7814e45570edf0024a1a5c2ba9fbc9cb3a49f7f7
