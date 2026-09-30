# [H] electerm has Path Traversal in Zmodem and Trzsz Download Filename Handling

## Summary
Severity: High
Advisory: GHSA-38j7-23hf-9mhc
CVE: CVE-2026-49253
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-38j7-23hf-9mhc
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0 <3.11.11

## Details
### Impact

A path traversal vulnerability exists in the Zmodem and Trzsz file download handlers in electerm. When receiving files via Zmodem or Trzsz protocols, electerm uses the remote-supplied filename directly in `path.join()` with the user-selected download directory without sanitization.

A malicious SSH server or remote shell process can send a specially crafted filename such as `../escaped.txt` to escape the user-selected download directory and write files to arbitrary locations on the user's filesystem, subject to process permissions.

**Attack scenario:**
1. User connects to a malicious SSH server
2. Attacker initiates a Zmodem or Trzsz file transfer
3. Attacker supplies a traversal filename (e.g., `../../.bashrc`, `../escaped.txt`)
4. User accepts the transfer and selects a download directory
5. File is written outside the selected directory, potentially overwriting sensitive files

**Affected components:**
- `src/app/server/zmodem.js` - `prepareReceiveFile()` at line 736
- `src/app/server/trzsz.js` - `getUniqueFilePath()` at line 559, `openSaveFile()` callback, and `savedFilePaths` mapping

### Patches

- https://github.com/electerm/electerm/commit/fde153d677a170c5816368f6586647f3af4ef284

### Workarounds


If upgrading is not immediately possible, users can mitigate this vulnerability by:
1. Only connecting to trusted SSH servers
2. Rejecting or canceling any incoming Zmodem or Trzsz file transfers from untrusted sources
3. Avoiding the use of Zmodem (`sz`/`rz`) and Trzsz (`trz`/`tsz`) commands on untrusted servers

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-38j7-23hf-9mhc
- https://github.com/electerm/electerm/commit/fde153d677a170c5816368f6586647f3af4ef284
- https://github.com/electerm/electerm
