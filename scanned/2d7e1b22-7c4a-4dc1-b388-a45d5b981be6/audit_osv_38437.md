# [H] Sleuth Kit tsk_recover Path Traversal

## Summary
Severity: High
Advisory: CVE-2026-40024
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-40024
Type: osv

## Details
The Sleuth Kit through 4.14.0 contains a path traversal vulnerability in tsk_recover that allows an attacker to write files to arbitrary locations outside the intended recovery directory via crafted filenames or directory paths with path traversal sequences in a filesystem image. An attacker can craft a malicious filesystem image with embedded /../ sequences in filenames that, when processed by tsk_recover, writes files outside the output directory, potentially achieving code execution by overwriting shell configuration or cron entries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40024.json
- https://mobasi.ai/sentinel
- https://nvd.nist.gov/vuln/detail/CVE-2026-40024
- https://www.vulncheck.com/advisories/sleuth-kit-tsk-recover-path-traversal
- https://github.com/sleuthkit/sleuthkit/commit/a3f96b3bc36a8bb1a00c297f77110d4a6e7dd31b
