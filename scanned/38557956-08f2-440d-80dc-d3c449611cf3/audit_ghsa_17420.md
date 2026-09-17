# [H] Self-hosted n8n has Legacy Code node that enables arbitrary file read/write

## Summary
Severity: High
Advisory: GHSA-j4p8-h8mh-rh8q
CVE: CVE-2025-68697
CWE: CWE-269, CWE-749
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-j4p8-h8mh-rh8q
Type: github-advisory

## Affected
- npm: `n8n` — affected >=1.2.1 <2.0.0

## Details
### Impact

In self-hosted n8n instances where the Code node runs in legacy (non-task-runner) JavaScript execution mode, authenticated users with workflow editing access can invoke internal helper functions from within the Code node.

This allows a workflow editor to perform actions on the n8n host with the same privileges as the n8n process, including:

- Reading files from the host filesystem (subject to any file-access restrictions configured on the instance and OS/container permissions)
- Writing files to the host filesystem (subject to the same restrictions)

Starting with n8n version 1.2.1, access to files in the n8n home directory (`.n8n`) is blocked by default. However, this does not restrict access to other parts of the filesystem unless additional file access limitations are configured.

### Patches

- Upgrade to **n8n version 2.0.0 or later**, where task runners are enabled by default for Code node execution.
- On **n8n version 1.71.0 and above**, enable task runners by setting `N8N_RUNNERS_ENABLED=true`.

### Workarounds

If you cannot immediately migrate to task runners:

- Limit file operations by setting `N8N_RESTRICT_FILE_ACCESS_TO` to a dedicated directory (e.g., `~/.n8n-files`) and ensure it contains no sensitive data.
- Keep `N8N_BLOCK_FILE_ACCESS_TO_N8N_FILES=true` (default) to block access to `.n8n` and user-defined config files.
- If workflow editors are not fully trusted, consider disabling high-risk nodes (including the Code node) using `NODES_EXCLUDE`.

### Resources

- n8n Docs: [Task runners](https://docs.n8n.io/hosting/configuration/task-runners/)
- n8n Docs: [Task runner environment variables](https://docs.n8n.io/hosting/configuration/environment-variables/task-runners/)
- n8n Docs: [Security environment variables](https://docs.n8n.io/hosting/configuration/environment-variables/security/#security-environment-variables)
- n8n Docs: [v2.0 breaking changes](https://docs.n8n.io/2-0-breaking-changes/#enable-task-runners-by-default)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-j4p8-h8mh-rh8q
- https://nvd.nist.gov/vuln/detail/CVE-2025-68697
- https://github.com/n8n-io/n8n
