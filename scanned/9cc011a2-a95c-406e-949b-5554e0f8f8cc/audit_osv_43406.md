# [C] Cockpit CMS 2.14.0 Authenticated Command Injection via FFmpeg Filename

## Summary
Severity: Critical
Advisory: CVE-2026-73680
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-73680
Type: osv

## Details
Cockpit CMS 2.14.0 and prior contains a command injection vulnerability in the FFmpeg integration that allows authenticated users with only the assets/upload permission to execute arbitrary commands by uploading a video file with a shell metacharacter-laden filename. The unsanitized filename is interpolated into a shell command executed via Process::fromShellCommandline() before the slugify() sanitizer runs, enabling injected shell metacharacters such as backticks, $(), and semicolons to escape the FFmpeg command context and execute as the web-server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73680.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73680
- https://www.vulncheck.com/advisories/cockpit-cms-authenticated-command-injection-via-ffmpeg-filename
- https://github.com/Cockpit-HQ/Cockpit/commit/28813596f57685f63d3a48f655e8e9bd2b535cab
- https://github.com/Cockpit-HQ/Cockpit
- https://link.mateocallec.com/MFC-2026-002
