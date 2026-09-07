# [H] electerm has Command Injection in File System Operations (rmrf, mv, cp)

## Summary
Severity: High
Advisory: GHSA-v5ff-xmfp-p245
CVE: CVE-2026-49255
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-v5ff-xmfp-p245
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0 <3.11.11

## Details
### Impact

A command injection vulnerability exists in electerm's file system operations (`rmrf`, `mv`, `cp`) in `src/app/lib/fs.js`. These functions construct shell commands by interpolating file paths directly into command strings without escaping shell metacharacters.

**Vulnerable functions:**
- `rmrf()` - Uses `rm -rf "${path}"` (double quotes, vulnerable to `"` injection)
- `mv()` - Uses `mv '${from}' '${to}'` (single quotes, vulnerable to `'` injection)
- `cp()` - Uses `cp -r "${from}" "${to}"` (double quotes, vulnerable to `"` injection)

**Attack scenario:**
1. Attacker controls a malicious SSH/SFTP server
2. Server lists files with shell metacharacters in names (e.g., `file"$(touch /tmp/pwned)"`)
3. Victim connects to the server and performs file operations (remote-to-local transfer, rename on conflict, etc.)
4. The malicious filename is passed to `rmrf()`, `mv()`, or `cp()` without sanitization
5. Shell metacharacters break out of the quoted argument and execute arbitrary commands

**Impact includes:**
- Arbitrary command execution as the electerm desktop user
- Data exfiltration, malware installation, or system compromise
- Both POSIX (bash) and Windows (PowerShell) platforms are affected

### Patches

- https://github.com/electerm/electerm/commit/aa778818843b9c083bd711cd04644d102fcb5a42

### Workarounds

If upgrading is not immediately possible, users can mitigate this vulnerability by:
1. Only connecting to trusted SSH/SFTP servers
2. Avoiding remote-to-local file transfers from untrusted sources
3. Not using the "rename on conflict" option when downloading folders from untrusted servers
4. Manually verifying filenames before performing file operations

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-v5ff-xmfp-p245
- https://github.com/electerm/electerm/commit/aa778818843b9c083bd711cd04644d102fcb5a42
- https://github.com/electerm/electerm
