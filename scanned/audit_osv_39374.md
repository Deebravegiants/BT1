# [M] Open WebUI: An IDOR vulnerability exists in the pin_channel_message API endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-45386
Aliases: GHSA-5gc6-xhv4-2wg6, PYSEC-2026-2705
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-45386
Type: osv

## Details
Open WebUI is a self-hosted artificial intelligence platform designed to operate entirely offline. Prior to 0.9.5, Pin/Unpin is a write operation (modifies the message's is_pinned , pinned_by, pinned_at fields), but in standard channels it only checks read permission, allowing users with read-only access to pin/unpin any message. This vulnerability is fixed in 0.9.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45386.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-5gc6-xhv4-2wg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45386
