# [H] FreeSWITCH: Pre-authentication bandwidth amplification via `mod_verto` speed-test frames

## Summary
Severity: High
Advisory: CVE-2026-49842
Aliases: GHSA-p3gx-p2w7-wp35
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49842
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.11.1, mod_verto's WebSocket frame loop intercepts a #-prefixed speed-test protocol (#SPU / #SPB / #SPE) before any authentication check. The declared payload size in #SPU was parsed with atoi() and only rejected non-positive values, so an unauthenticated peer could request up to INT_MAX bytes. The server then wrote roughly size * 10 bytes back during the download phase, on the order of 20 GB per request, yielding strong outbound bandwidth amplification from a short request. This issue has been patched in version 1.11.1.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49842.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-p3gx-p2w7-wp35
- https://nvd.nist.gov/vuln/detail/CVE-2026-49842
