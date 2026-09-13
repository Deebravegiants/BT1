# [C] n8n Vulnerable to Arbitrary Command Execution in Pyodide based Python Code Node 

## Summary
Severity: Critical
Advisory: GHSA-62r4-hw23-cc8v
CVE: CVE-2025-68668
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-62r4-hw23-cc8v
Type: github-advisory

## Affected
- npm: `n8n` — affected >=1.0.0 <2.0.0

## Details
### Impact
A sandbox bypass vulnerability exists in the Python Code Node that uses Pyodide.

An authenticated user with permission to create or modify workflows can exploit this vulnerability to execute arbitrary commands on the host system running n8n, using the same privileges as the n8n process.

### Patches
In n8n version 1.111.0, a task-runner-based native Python implementation was introduced as an optional feature, providing a more secure isolation model.

To enable it, you need to configure the `N8N_RUNNERS_ENABLED` and `N8N_NATIVE_PYTHON_RUNNER` environment variables.

This implementation became the default starting with n8n version 2.0.0.

### Workarounds
- Disable the Code Node by setting the environment variable `NODES_EXCLUDE: "[\"n8n-nodes-base.code\"]"` ([Docs)](https://docs.n8n.io/hosting/securing/blocking-nodes/)
- Disable Python support in the Code node by setting the environment variable `N8N_PYTHON_ENABLED=false`, which was introduced in n8n version 1.104.0.
- Configure n8n to use the task runner based Python sandbox via the `N8N_RUNNERS_ENABLED` and `N8N_NATIVE_PYTHON_RUNNER` environment variables. ([Docs](https://docs.n8n.io/hosting/configuration/task-runners/))

### Resources
- n8n documentation: [Blocking access to nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/)
- n8n documentation: [Code Node (Python)](https://docs.n8n.io/code/code-node/#python-native)
- n8n documentation: [Task Runners](https://docs.n8n.io/hosting/configuration/task-runners/)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-62r4-hw23-cc8v
- https://nvd.nist.gov/vuln/detail/CVE-2025-68668
- https://github.com/n8n-io/n8n
- https://www.smartkeyss.com/post/cve-2025-68668-breaking-out-of-the-python-sandbox-in-n8n
