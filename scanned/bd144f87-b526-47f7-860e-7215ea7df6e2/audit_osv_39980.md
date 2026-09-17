# [M] Notepad++ WM_COPYDATA COPYDATA_FULL_CMDLINE local DoS crash

## Summary
Severity: Medium
Advisory: CVE-2026-48770
Aliases: GHSA-r39g-3mcw-xcg2
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-48770
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.6.1, a local process in the same interactive Windows session can send a malformed WM_COPYDATA message to Notepad++ using the COPYDATA_FULL_CMDLINE path. The handler appears to process COPYDATASTRUCT.lpData as an unbounded NUL-terminated wchar_t* instead of enforcing COPYDATASTRUCT.cbData. This vulnerability is fixed in 8.9.6.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48770.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-r39g-3mcw-xcg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48770
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/f20a0888a92ce557a339b833cd9d9d8e97dc797d
