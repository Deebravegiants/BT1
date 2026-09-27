# [H] Electerm has an unvalidated shell.openExternal that allows arbitrary protocol execution via terminal link click

## Summary
Severity: High
Advisory: GHSA-fwf6-j56g-m97c
CVE: CVE-2026-43941
CWE: CWE-601, CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-fwf6-j56g-m97c
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0

## Details
### Impact

Electerm's terminal hyperlink handler passes any URL clicked in the terminal directly to `shell.openExternal` without any protocol validation.

When a user connects to a malicious SSH server, the attacker can print a crafted URI in the terminal output. If the victim clicks the link, `shell.openExternal` executes it using the operating system's default protocol handler.

This can be abused to:
- Trigger dangerous protocol handlers (`ms-msdt:`, `search-ms:`) for code execution
- Open local files or network shares (`file://`, UNC paths) to leak NTLM hashes or exfiltrate data
- Launch any installed application associated with a custom URI scheme

An attacker who controls terminal output (e.g., via a malicious SSH server, compromised remote host, or malicious plugin rendering terminal content) can thus achieve arbitrary code execution or local file access on the victim's machine, requiring only that the victim clicks a displayed link.

### Patches

As of electerm v3.7.9, no official patch has been released. Users should monitor the project’s [GitHub releases](https://github.com/electerm/electerm/releases) and [security page](https://github.com/electerm/electerm/security) for an update addressing this issue.

### Workarounds

Until a patch is available:
- Do not click on any links displayed in terminal sessions connected to untrusted servers.
- If possible, disable hyperlink rendering in electerm's terminal settings.
- Use a terminal multiplexer (e.g., tmux) or a separate terminal application that filters URI schemes when working with untrusted hosts.
- Consider running electerm in a restricted environment (sandbox, AppArmor, SELinux) that limits the spawning of protocol handlers.

### Resources

- [electerm GitHub Repository](https://github.com/electerm/electerm)
- [electerm Security Policy](https://github.com/electerm/electerm/security)
- Vulnerability details originally reported by external researcher (confirmed on v3.7.9, Win10).

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-fwf6-j56g-m97c
- https://nvd.nist.gov/vuln/detail/CVE-2026-43941
- https://github.com/electerm/electerm
