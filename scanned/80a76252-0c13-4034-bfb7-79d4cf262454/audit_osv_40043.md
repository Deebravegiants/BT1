# [M] Gradio < 6.16.0 Path Traversal via FileExplorer.preprocess()

## Summary
Severity: Medium
Advisory: CVE-2026-49119
Aliases: PYSEC-2026-2179
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-49119
Type: osv

## Details
Gradio before 6.16.0 contain a path traversal vulnerability in the FileExplorer component's preprocess() method that allows unauthenticated attackers to escape the configured root directory by supplying path segments containing directory traversal sequences or absolute paths. Attackers can provide crafted path segments that cause os.path.join to discard the root_dir prefix entirely, resulting in arbitrary file read or exposure of sensitive files outside the intended directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49119.json
- https://github.com/gradio-app/gradio/releases/tag/gradio%406.16.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-49119
- https://www.vulncheck.com/advisories/gradio-path-traversal-via-fileexplorer-preprocess
- https://github.com/gradio-app/gradio/pull/13437
- https://github.com/gradio-app/gradio/commit/97d541f3d5fd05b2587a69ecc94b68fe5d2d7004
- https://github.com/gradio-app/gradio
