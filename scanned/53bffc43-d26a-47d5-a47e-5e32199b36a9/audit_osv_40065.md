# [H] Jellyfin: Potential Authenticated path traversal in /ClientLog/Document

## Summary
Severity: High
Advisory: CVE-2026-49247
Aliases: GHSA-jg92-mrxq-vv75
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-49247
Type: osv

## Details
Jellyfin is an open source self hosted media server. From 10.9.0 until 10.11.10, the POST /ClientLog/Document endpoint accepts the Authorization header's Client and Version fields and uses them unsanitized as components of the on-disk filename when persisting client-uploaded log documents. As a result, any authenticated non-admin user can include ../ sequences in the Client field to cause Jellyfin to write attacker-controlled content to arbitrary paths reachable by the Jellyfin service user, with a forced .log suffix. This vulnerability is fixed in 10.11.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49247.json
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-jg92-mrxq-vv75
- https://nvd.nist.gov/vuln/detail/CVE-2026-49247
