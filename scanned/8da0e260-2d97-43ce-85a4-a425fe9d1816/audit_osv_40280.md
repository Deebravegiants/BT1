# [C] Notepad++ TOCTOU: HMAC Checks Disk, Executes from Memory

## Summary
Severity: Critical
Advisory: CVE-2026-52885
Aliases: GHSA-qm4c-qg8p-qfcr
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-52885
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.6.4, NppCommands.cpp checks the HMAC of the on-disk shortcuts.xml at the moment a user command fires (Time-of-Check). However, the command payload is taken from the in-memory _userCommands vector, which is populated at application startup and never re-synchronized with the on-disk file (Time-of-Use). Swapping shortcuts.xml between startup and command execution causes the HMAC check to validate a clean file while a malicious command runs. An attacker with write access to shortcuts.xml places a malicious version on disk before launch, then immediately restores the legitimate file. The HMAC check at execution time validates the restored legitimate file (check passes), while the malicious payload executes from memory. This vulnerability is fixed in 8.9.6.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52885.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-qm4c-qg8p-qfcr
- https://nvd.nist.gov/vuln/detail/CVE-2026-52885
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/4f7563c7c7f8ffa0d795ec86a7777067c7d644b5
