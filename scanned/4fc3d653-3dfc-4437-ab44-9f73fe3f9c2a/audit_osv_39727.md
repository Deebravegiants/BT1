# [C] IINA < 1.4.3 Command Execution via iina://open URL Scheme

## Summary
Severity: Critical
Advisory: CVE-2026-47114
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-47114
Type: osv

## Details
IINA before 1.4.3 contains a user-assisted command execution vulnerability that allows remote attackers to execute arbitrary commands by supplying malicious mpv_-prefixed query parameters through the iina://open custom URL scheme handler. Attackers can deliver a crafted URL via a browser that passes unvalidated mpv_options/input-commands parameters into the mpv runtime, causing arbitrary command execution as the current macOS user upon approval of the browser protocol prompt without requiring a valid media file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47114.json
- https://github.com/iina/iina/releases/tag/v1.4.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-47114
- https://www.vulncheck.com/advisories/iina-command-execution-via-iina-open-url-scheme
- https://github.com/iina/iina/commit/1e6f43248dab9d6ae303781c790e5315cbc9fcef
- https://github.com/iina/iina
- https://binary.stackpointer.re/iina-142-url-scheme-command-execution
