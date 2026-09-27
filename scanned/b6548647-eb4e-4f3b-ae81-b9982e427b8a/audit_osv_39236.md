# [H] Pi-hole FTL: Unauthenticated Session Hijacking via Race Condition on Global Session Buffer

## Summary
Severity: High
Advisory: CVE-2026-44693
Aliases: GHSA-9ff5-f3v5-2xc7
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-44693
Type: osv

## Details
Pi-hole FTL is the core engine of the Pi-hole network-level advertisement and tracker blocker. Prior to version 6.6.1, Pi-hole FTL contains a race condition vulnerability in the HTTP session management subsystem, introduced with the v6.0 rewrite of the embedded CivetWeb-based web server. This issue has been patched in version 6.6.1.

## References
- https://github.com/pi-hole/FTL/releases/tag/v6.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44693.json
- https://github.com/pi-hole/FTL/security/advisories/GHSA-9ff5-f3v5-2xc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44693
