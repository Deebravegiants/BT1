# [M] Directory traversal allowing overwriting arbitrary files

## Summary
Severity: Medium
Advisory: CVE-2024-30254
Aliases: GHSA-48c5-35fh-846h
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-30254
Type: osv

## Details
MesonLSP is an unofficial, unendorsed language server for meson written in C++. A vulnerability in versions prior to 4.1.4 allows overwriting arbitrary files if the attacker can make the victim either run the language server within a specific crafted project or `mesonlsp --full`. Version 4.1.4 contains a patch for this issue. As a workaround, avoid running `mesonlsp --full` and set the language server option `others.neverDownloadAutomatically` to `true`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30254.json
- https://github.com/JCWasmx86/mesonlsp/security/advisories/GHSA-48c5-35fh-846h
- https://nvd.nist.gov/vuln/detail/CVE-2024-30254
- https://github.com/JCWasmx86/mesonlsp/commit/594b6334061371911cd59389124ab8af30ce0a3a
