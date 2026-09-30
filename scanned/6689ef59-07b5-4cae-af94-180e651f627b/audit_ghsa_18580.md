# [M] n8n is vulnerable to Improper Authorization through its `/stop` endpoint

## Summary
Severity: Medium
Advisory: GHSA-gq57-v332-7666
CVE: CVE-2025-52554
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-07-03
Source: https://github.com/advisories/GHSA-gq57-v332-7666
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.99.1

## Details
## Summary

An authorization vulnerability was discovered in the `/rest/executions/:id/stop` endpoint of n8n. An authenticated user can stop workflow executions that they do not own or that have not been shared with them, leading to potential business disruption.

### Impact

This is an **improper authorization** vulnerability. While most API methods enforce user-scoped access to workflow execution IDs, the `/stop` endpoint fails to do so. An attacker can guess or enumerate execution IDs (which are sequential and partially exposed via verbose error messages) and terminate active workflows initiated by other users.

**Who is impacted:**
- Environments where multiple users with varying trust levels share access to the same n8n instance.
- All users running long-running or time-sensitive workflows (e.g., using the `wait` node).

An attacker with authenticated access can exploit this flaw to:
- Disrupt other users’ workflow executions.
- Cause denial of service for business-critical automations.

### Patches

The issue was addressed in https://github.com/n8n-io/n8n/pull/16405. Users should upgrade to version >= 1.99.1.

Users should upgrade to this version or later to ensure proper authorization checks are enforced before stopping workflow executions.

### Workarounds

To mitigate this issue without upgrading:
- Restrict access to the `/rest/executions/:id/stop` endpoint via reverse proxy or API gateway.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-gq57-v332-7666
- https://nvd.nist.gov/vuln/detail/CVE-2025-52554
- https://github.com/n8n-io/n8n/pull/16405
- https://github.com/dudanogueira/n8n/commit/ca2f90c7fbaa1d661ade2f45d587d9469bc287e1
- https://github.com/n8n-io/n8n/commit/e5edc60e344924230baafb11fa1f0af788e9ca9a
- https://github.com/n8n-io/n8n
