# [M] Bulwark Webmail: Authentication Bypass in verifyIdentity() due to missing cookie validation

## Summary
Severity: Medium
Advisory: CVE-2026-34834
Aliases: GHSA-4356-876g-rfmh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34834
Type: osv

## Details
Bulwark Webmail is a self-hosted webmail client for Stalwart Mail Server. Prior to version 1.4.10, the verifyIdentity() function contained logic that returned true if no session cookies were present. This allowed unauthenticated attackers to bypass security checks and access/modify user settings via the /api/settings endpoint by providing arbitrary headers. This issue has been patched in version 1.4.10.

## References
- https://github.com/bulwarkmail/webmail/releases/tag/1.4.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34834.json
- https://github.com/bulwarkmail/webmail/security/advisories/GHSA-4356-876g-rfmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34834
