# [H] Jellyfin: Potential SSRF + Arbitrary file read via LiveTV M3U tuner

## Summary
Severity: High
Advisory: CVE-2026-35032
Aliases: GHSA-8fw7-f233-ffr8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-35032
Type: osv

## Details
Jellyfin is an open source self hosted media server. Versions prior to 10.11.7 contain a vulnerability chain in the LiveTV M3U tuner endpoint (POST /LiveTv/TunerHosts), where the tuner URL is not validated, allowing local file read via non-HTTP paths and Server-Side Request Forgery (SSRF) via HTTP URLs. This is exploitable by any authenticated user because the EnableLiveTvManagement permission defaults to true for all new users. An attacker can chain these vulnerabilities by adding an M3U tuner pointing to an attacker-controlled server, serving a crafted M3U with a channel pointing to the Jellyfin database, exfiltrating the database to extract admin session tokens, and escalating to admin privileges. This issue has been fixed in version 10.11.7. If users are unable to upgrade immediately, they can disable Live TV Management privileges for all users.

## References
- https://github.com/jellyfin/jellyfin/releases/tag/v10.11.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35032.json
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-8fw7-f233-ffr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-35032
