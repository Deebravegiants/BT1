# [H] Sonarr Authentication Bypass vulnerability

## Summary
Severity: High
Advisory: CVE-2026-30975
Aliases: GHSA-h5qx-5hjf-7c9r
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-30975
Type: osv

## Details
Sonarr is a PVR for Usenet and BitTorrent users. Versions prior to 4.0.16.2942 have an authentication bypass that affected users that had disabled authentication for local addresses (Authentication Required set to: `Disabled for Local Addresses`) without a reverse proxy running in front of Sonarr that didn't not pass through the invalid header. Patches are available in version 4.0.16.2942 in the nightly/develop branch and version 4.0.16.2944 for stable/main releases. Some workarounds are available. Make sure Sonarr's Authentication Required setting is set to `Enabled`, run Sonarr behind a reverse proxy, and/or do not expose Sonarr directly to the internet and instead rely on accessing it through a VPN, Tailscale or a similar solution.

## References
- https://github.com/Sonarr/Sonarr/releases/tag/v4.0.16.2942
- https://github.com/Sonarr/Sonarr/releases/tag/v4.0.16.2944
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30975.json
- https://github.com/Sonarr/Sonarr/security/advisories/GHSA-h5qx-5hjf-7c9r
- https://nvd.nist.gov/vuln/detail/CVE-2026-30975
