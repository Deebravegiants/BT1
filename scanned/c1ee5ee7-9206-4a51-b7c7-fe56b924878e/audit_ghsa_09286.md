# [H] Open WebUI: Redis Cache Keys tool_servers and terminal_servers Missing Instance Prefix Enable Cross-Instance Cache Poisoning

## Summary
Severity: High
Advisory: GHSA-3x8w-4f7p-xxc2
CVE: CVE-2026-44552
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-3x8w-4f7p-xxc2
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
# Redis Cache Keys tool_servers and terminal_servers Missing Instance Prefix Enable Cross-Instance Cache Poisoning

## Affected Component

Tool server and terminal server Redis cache:
- `backend/open_webui/utils/tools.py` (line 841, tool_servers SET)
- `backend/open_webui/utils/tools.py` (line 850, tool_servers GET)
- `backend/open_webui/utils/tools.py` (line 976, terminal_servers SET)
- `backend/open_webui/utils/tools.py` (line 986, terminal_servers GET)

## Affected Versions

Current main branch (commit `6fdd19bf1`) and likely all versions since the tool server / terminal server Redis cache was introduced.

## Description

Open WebUI uses a `REDIS_KEY_PREFIX` (default `open-webui`) to namespace Redis keys, allowing multiple instances to safely share a single Redis backend. Every Redis key in the codebase uses this prefix — except the `tool_servers` and `terminal_servers` keys in `utils/tools.py`, which use bare key names.

When two or more Open WebUI instances share a Redis database (a supported and documented deployment pattern, e.g., for multi-region deployments, blue-green setups, or cluster topologies), the unprefixed keys collide. An admin on Instance A writing to `tool_servers` overwrites the value read by Instance B — causing Instance B's users to receive Instance A's tool server configuration.

```python
# utils/tools.py — unprefixed keys (problem)
await request.app.state.redis.set('tool_servers', ...)        # line 841
json.loads(await request.app.state.redis.get('tool_servers')) # line 850
await request.app.state.redis.set('terminal_servers', ...)    # line 976
json.loads(await request.app.state.redis.get('terminal_servers'))  # line 986

# Every other Redis key in the codebase — prefixed (correct pattern)
f'{REDIS_KEY_PREFIX}:auth:token:{jti}:revoked'
f'{REDIS_KEY_PREFIX}:ratelimit:{email}:{bucket}'
f'{REDIS_KEY_PREFIX}:tasks:commands'
```

## Attack Scenario

Two Open WebUI instances (A and B) share a Redis backend — a supported deployment for multi-region setups, blue-green deployments, or hot-standby. Both instances have their own admin accounts; the shared Redis was chosen for coordinated session handling, rate limiting, and task management.

1. Attacker is an admin on Instance A (a legitimately provisioned admin, or one that escalated via any available path including the LDAP empty-password or stale-admin-role findings).
2. Attacker on Instance A configures a tool server pointing to `https://attacker-controlled.example.com/openapi.json`. This triggers `utils/tools.py:841` to write the new tool server list under the bare key `tool_servers`.
3. Instance B's users query tools. Instance B reads from `tool_servers` (line 850) — gets Instance A's poisoned list, which now includes the attacker's server alongside or instead of Instance B's legitimate tool servers.
4. Instance B's users invoke tools through the model's context. The attacker's server receives tool call payloads containing: chat content, user identity, OAuth tokens scoped to the tool server (if the user has bound their external account), and in-flight conversation context.
5. The attacker's server returns arbitrary tool responses, which are fed back into Instance B's LLM context as "trusted tool output" — enabling prompt injection, misinformation delivery, and further data exfiltration cascades.

The same cross-instance poisoning applies to `terminal_servers`.

## Impact

- Cross-instance cache poisoning: an admin on one instance affects all users of another instance sharing the Redis backend
- Data exfiltration: tool call payloads contain chat content and user identity, delivered to the attacker's server
- Prompt injection delivery: attacker-returned tool responses enter the victim instance's LLM context as trusted data
- Undermines the multi-instance isolation guarantee that `REDIS_KEY_PREFIX` was introduced to provide
- Silent failure mode: no error is raised; the victim instance sees a valid, signed cache entry and has no way to detect it came from a different instance

## Preconditions

- Multiple Open WebUI instances share a single Redis backend (a supported and documented deployment)
- Attacker has admin access on one of the instances (or escalates to admin via any available path)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3x8w-4f7p-xxc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44552
- https://github.com/open-webui/open-webui
