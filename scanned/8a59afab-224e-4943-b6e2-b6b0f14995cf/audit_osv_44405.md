# [H] CVE-2026-82217

## Summary
Severity: High
Advisory: CVE-2026-82217
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82217
Type: osv

## Details
In Eclipse Theia versions 1.73.0 up to but not including 1.75.0, the AI "Agent Mode" file-change tools (writeFileContent, suggestFileContent, and the replacement and state helpers) resolved a model-supplied file path without a workspace-containment check. A crafted relative path such as ../.bashrc, an absolute path, or a ~-expanded path could therefore write or delete files outside the workspace with the privileges of the Theia backend OS user. Because the path argument is influenced by model output, it can be steered through indirect prompt injection, and in Agent Mode writes are applied without a confirmation dialog. Writing to a host-executed file such as a shell startup file or ~/.ssh/authorized_keys can escalate to code execution on the backend.

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/624
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82217.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82217
- https://github.com/eclipse-theia/theia/commit/28da106c254
