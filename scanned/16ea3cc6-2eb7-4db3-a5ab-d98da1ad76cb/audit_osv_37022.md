# [M] calibre has IP Ban Bypass via X-Forwarded-For Header Spoofing

## Summary
Severity: Medium
Advisory: CVE-2026-27824
Aliases: GHSA-vhxc-r7v8-2xrw
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-27824
Type: osv

## Details
calibre is a cross-platform e-book manager for viewing, converting, editing, and cataloging e-books. Prior to version 9.4.0, the calibre Content Server's brute-force protection mechanism uses a ban key derived from both `remote_addr` and the `X-Forwarded-For` header. Since the `X-Forwarded-For` header is read directly from the HTTP request without any validation or trusted-proxy configuration, an attacker can bypass IP-based bans by simply changing or adding this header, rendering the brute-force protection completely ineffective. This is particularly dangerous for calibre servers exposed to the internet, where brute-force protection is the primary defense against credential stuffing and password guessing attacks. Version 9.4.0 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27824.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-vhxc-r7v8-2xrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27824
