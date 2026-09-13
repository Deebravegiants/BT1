# [H] Unsafe symlink following in restricted workspace-write sandbox leads to RCE

## Summary
Severity: High
Advisory: CVE-2025-55345
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/CVE-2025-55345
Type: osv

## Details
Using Codex CLI in workspace-write mode inside a malicious context (repo, directory, etc) could lead to arbitrary file overwrite and potentially remote code execution due to symlinks being followed outside the allowed current working directory.

## References
- https://www.npmjs.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55345.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55345
- https://research.jfrog.com/vulnerabilities/codex-cli-symlink-arbitrary-file-overwrite-jfsa-2025-001378631/
- https://github.com/openai/codex/pull/1705
