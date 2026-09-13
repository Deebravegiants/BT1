# [C] Tabby: RCE via `tabby://run` URL Scheme

## Summary
Severity: Critical
Advisory: CVE-2026-45035
Aliases: GHSA-hf8h-rjrf-3jg6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-45035
Type: osv

## Details
Tabby (formerly Terminus) is a highly configurable terminal emulator. Prior to 1.0.233, Tabby registers itself as the handler for the tabby:// URL scheme on all platforms. The URL scheme handler supports a run command that directly executes OS commands with no user confirmation, sanitization, or sandboxing. An attacker can craft a malicious link (tabby://run?command=...) and deliver it via a website, email, chat message, or any other medium. When a victim clicks the link, the OS launches Tabby which immediately spawns the specified command as a child process with the user's full privileges. This is a zero-click-after-link-visit RCE vulnerability. This vulnerability is fixed in 1.0.233.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45035.json
- https://github.com/Eugeny/tabby/security/advisories/GHSA-hf8h-rjrf-3jg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45035
