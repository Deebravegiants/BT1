# [H] Jellyfin: Potential SSRF + Arbitrary file read via stream argument injection

## Summary
Severity: High
Advisory: CVE-2026-35033
Aliases: GHSA-jh22-fw8w-2v9x
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-35033
Type: osv

## Details
Jellyfin is an open source self hosted media server. Versions prior to 10.11.7 contain an unauthenticated arbitrary file read vulnerability via ffmpeg argument injection through the StreamOptions query parameter parsing mechanism. The ParseStreamOptions method in StreamingHelpers.cs adds any lowercase query parameter to a dictionary without validation, bypassing the RegularExpression attribute on the level controller parameter, and the unsanitized value is concatenated directly into the ffmpeg command line. By injecting a drawtext filter with a textfile argument, an attacker can read arbitrary server files such as /etc/shadow and exfiltrate their contents as text rendered in the video stream response. The vulnerable /Videos/{itemId}/stream endpoint has no Authorize attribute, making this exploitable without authentication, though item GUIDs are pseudorandom and require an authenticated user to obtain. This issue has been fixed in version 10.11.7.

## References
- https://github.com/jellyfin/jellyfin/releases/tag/v10.11.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35033.json
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-jh22-fw8w-2v9x
- https://nvd.nist.gov/vuln/detail/CVE-2026-35033
