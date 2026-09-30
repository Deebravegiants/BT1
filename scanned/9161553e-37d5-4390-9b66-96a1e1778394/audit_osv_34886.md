# [C] StreamVault is Vulnerable to Authenticated Remote Code Execution (RCE) via ytdlpargs Configuration Injection

## Summary
Severity: Critical
Advisory: CVE-2025-66203
Aliases: GHSA-c747-q388-3v6m
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-26
Source: https://osv.dev/vulnerability/CVE-2025-66203
Type: osv

## Details
StreamVault is a video download integration solution. Prior to version 251126, a Remote Code Execution (RCE) vulnerability exists in the stream-vault application (SpiritApplication). The application allows administrators to configure yt-dlp arguments via the /admin/api/saveConfig endpoint without sufficient validation. These arguments are stored globally and subsequently used in YtDlpUtil.java when constructing the command line to execute yt-dlp. This issue has been patched in version 251126.

## References
- https://github.com/lemon8866/StreamVault/releases/tag/251226
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66203.json
- https://github.com/lemon8866/StreamVault/security/advisories/GHSA-c747-q388-3v6m
- https://nvd.nist.gov/vuln/detail/CVE-2025-66203
