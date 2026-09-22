# [C] Neuron MySQLWriteTool allows arbitrary/destructive SQL when exposed to untrusted prompts (agent “footgun”)

## Summary
Severity: Critical
Advisory: GHSA-898v-775g-777c
CVE: CVE-2025-67510
CWE: CWE-250, CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-898v-775g-777c
Type: github-advisory

## Affected
- Packagist: `neuron-core/neuron-ai` — affected >=0 <2.8.12

## Details
### Impact

`MySQLWriteTool` executes arbitrary SQL provided by the caller using `PDO::prepare()` + `execute()` without semantic restrictions.  

This is consistent with the name (“write tool”), but in an LLM/agent context it becomes a high-risk capability: prompt injection or indirect prompt manipulation can cause execution of destructive queries such as `DROP TABLE`, `TRUNCATE`, `DELETE`, `ALTER`, or privilege-related statements (subject to DB permissions).



**Who is impacted:** Deployments that expose an agent with `MySQLWriteTool` enabled to untrusted input and/or run the tool with a DB user that has broad privileges.

### Patches

**Not patched in:** 2.8.11  

Recommended improvements (even if keeping the tool intentionally powerful):

- Provide a safer API that supports only constrained operations (e.g., `insertRecord`, `updateRecord`) with allowlisted tables/columns.

- Add a policy/allowlist layer (e.g., allow only `INSERT`/`UPDATE` on selected tables; forbid `DROP/TRUNCATE/ALTER/GRANT`).

- Add optional review workflow: log + require human approval for high-risk statements; or “dry-run” mode.

- Document strongly that the tool must not be exposed to untrusted prompts without additional safeguards.



### Workarounds

- Do not enable `MySQLWriteTool` for public/untrusted agents.

- Use a dedicated DB user with **least privilege**:

  - no `DROP`, no `ALTER`, no `GRANT`, no access to sensitive tables unless necessary

- Add an application-layer policy rejecting high-risk statements (`DROP`, `TRUNCATE`, `ALTER`, `GRANT`, `REVOKE`, `CREATE USER`, etc.).

- Implement authorization gating for tool calls (RBAC, allow tool use only for trusted operators).

## References
- https://github.com/neuron-core/neuron-ai/security/advisories/GHSA-898v-775g-777c
- https://nvd.nist.gov/vuln/detail/CVE-2025-67510
- https://github.com/neuron-core/neuron-ai/commit/44bab85d92bf162898ee48d0bcef6ba0d29b59c9
- https://github.com/neuron-core/neuron-ai
- https://github.com/neuron-core/neuron-ai/releases/tag/2.8.12
