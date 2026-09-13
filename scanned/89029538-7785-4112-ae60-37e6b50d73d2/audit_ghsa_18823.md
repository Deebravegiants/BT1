# [H] n8n: Execute Command Node Allows Authenticated Users to Run Arbitrary Commands on Host

## Summary
Severity: High
Advisory: GHSA-365g-vjw2-grx8
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-365g-vjw2-grx8
Type: github-advisory

## Affected
- npm: `n8n-nodes-base` — affected >=0
- npm: `n8n` — affected >=0

## Details
### Impact

The `Execute Command` node in n8n allows execution of arbitrary commands on the host system where n8n runs. While this functionality is intended for advanced automation and can be useful in certain workflows, it poses a security risk if all users with access to the n8n instance are not fully trusted.

An attacker—either a malicious user or someone who has compromised a legitimate user account—could exploit this node to run arbitrary commands on the host machine, potentially leading to data exfiltration, service disruption, or full system compromise.

This vulnerability affects all n8n deployments where:

- The `Execute Command` node is enabled, and
- Not all user accounts are strictly controlled and trusted.

n8n.cloud is **not** impacted.


### Patches
No code changes have been made to alter the behavior of the `Execute Command` node. The recommended mitigation is to disable the node by default in environments where it is not explicitly required.

Future n8n versions may change the default availability of this node.

### Workarounds
Administrators can disable the `Execute Command` node by setting the following environment variable before starting n8n:

```bash
export NODES_EXCLUDE: "[\"n8n-nodes-base.executeCommand\"]"
```

### References
n8n docs: [Execute Command](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)
n8n docs: [Blocking nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-365g-vjw2-grx8
- https://github.com/n8n-io/n8n
