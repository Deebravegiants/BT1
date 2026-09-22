# [H] Malicious projects can read and upload arbitrary files from disk in TurboWarp Desktop

## Summary
Severity: High
Advisory: CVE-2023-40168
Aliases: GHSA-wg4p-vj7h-q82q
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2023-08-17
Source: https://osv.dev/vulnerability/CVE-2023-40168
Type: osv

## Details
TurboWarp is a desktop application that compiles scratch projects to JavaScript. TurboWarp Desktop versions prior to version 1.8.0 allowed a malicious project or custom extension to read arbitrary files from disk and upload them to a remote server. The only required user interaction is opening the sb3 file or loading the extension. The web version of TurboWarp is not affected. This bug has been addressed in commit `55e07e99b59` after an initial fix which was reverted. Users are advised to upgrade to version 1.8.0 or later. Users unable to upgrade should avoid opening sb3 files or loading extensions from untrusted sources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40168.json
- https://github.com/TurboWarp/desktop/security/advisories/GHSA-wg4p-vj7h-q82q
- https://nvd.nist.gov/vuln/detail/CVE-2023-40168
- https://github.com/TurboWarp/desktop/commit/55e07e99b59db334d75e8f46792a1569ab0884a6
- https://github.com/TurboWarp/desktop/commit/a62dbd7a28b41857e3b6f32443fda0527d493267
- https://github.com/TurboWarp/desktop/commit/f0f82aaf6cc8170e9da8b36953c98bfe533c019f
