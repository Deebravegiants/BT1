# [H] Jellyfin: Potential FFmpeg argument injection via unescaped subtitle file path

## Summary
Severity: High
Advisory: CVE-2026-48793
Aliases: GHSA-wwwm-px48-fpvq
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48793
Type: osv

## Details
Jellyfin is an open source self hosted media server. Prior to 10.11.10, a potential FFmpeg argument injection vulnerability exists in the subtitle conversion code path. SubtitleEncoder.ConvertTextSubtitleToSrtInternal (SubtitleEncoder.cs, line 382) interpolates the subtitle file path into FFmpeg command-line arguments without calling EncodingUtils.NormalizePath(). On Linux, filenames can contain double-quote characters, which break the argument quoting and allow injection of arbitrary FFmpeg arguments. The vulnerability is reachable without authentication via SubtitleController.GetSubtitle, which has no [Authorize] attribute. An attacker who can place a file in a Jellyfin media library directory (shared NAS, Samba share, guest upload) can achieve arbitrary file write on the server and information disclosure. This vulnerability is fixed in 10.11.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48793.json
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-wwwm-px48-fpvq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48793
