# [H] Detect-It-Easy < 3.21 Path Traversal Arbitrary File Write

## Summary
Severity: High
Advisory: CVE-2026-43616
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-43616
Type: osv

## Details
Detect-It-Easy prior to 3.21 contains a path traversal vulnerability that allows attackers to write arbitrary files to the filesystem by crafting malicious archive entries with relative traversal sequences or absolute paths. Attackers can exploit insufficient path normalization during archive extraction to write files outside the intended extraction directory and achieve persistent code execution by overwriting user startup scripts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43616.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43616
- https://www.vulncheck.com/advisories/detect-it-easy-path-traversal-arbitrary-file-write
- https://github.com/horsicq/DIE-engine/commit/7fd300b926daf19707b2a36f0abe8b60a51308ee
- https://github.com/horsicq/DIE-engine/commit/cbbe1688e58ffd430d284bf65f336973f083db69
- https://github.com/horsicq/DIE-engine/releases/tag/3.21
- https://github.com/horsicq/Formats/commit/56cdf50ee3c72c56284e2819b23e98332842d259
- https://github.com/horsicq/XArchive/commit/6a2aa84c2fd120b704f76bb5c5ee3e9b5a7a0fcc
- https://github.com/horsicq/Detect-It-Easy
