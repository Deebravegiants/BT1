# [H] Flowise: `DELETE /api/v1/chatflows/:id` does not validate resource type, allowing `agentflows:delete` and `chatflows:delete` to delete each other’s flow type

## Summary
Severity: High
Advisory: GHSA-p5w8-m249-4r4v
CVE: CVE-2026-69262
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-p5w8-m249-4r4v
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
# summary:
In Flowise, `DELETE /api/v1/chatflows/:id` authorizes requests with `checkAnyPermission('chatflows:delete,agentflows:delete')`. Possession of either permission is sufficient to reach the delete path. The delete logic does not validate the target resource `type`, allowing a caller with only `agentflows:delete` to delete a `CHATFLOW`, and a caller with only `chatflows:delete` to delete an `AGENTFLOW`.

# details:
The delete route accepts either `chatflows:delete` or `agentflows:delete`. The subsequent logic only resolves the target record by `id` and `workspaceId`, then deletes by `id` without checking whether the target resource type matches the granted permission domain.

As a result, there is no binding between permission scope and flow type:

- `agentflows:delete` can be used to delete `CHATFLOW`
- `chatflows:delete` can be used to delete `AGENTFLOW`

This breaks the intended RBAC separation between Chatflows and Agentflows.

# impact:
Users authorized to manage only one flow type can delete the other flow type within the same workspace, resulting in unauthorized deletion and configuration loss.

# reproduction steps:

1. Log in as a user who can create API keys.
2. Create a normal `CHATFLOW` and record its `id`.
3. Create an API key with only `agentflows:delete`.
4. Use that API key to send:

```bash
curl -i -X DELETE \
  -H 'Authorization: Bearer <agentflows_delete_only_key>' \
  http://localhost:8080/api/v1/chatflows/<chatflow_id>
```

5. Observe a `200 OK` response, for example:

```json
{"raw":[],"affected":1}
```

6. Read the same `id` again and observe `404 Not Found`.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-p5w8-m249-4r4v
- https://github.com/FlowiseAI/Flowise/pull/6445
- https://github.com/FlowiseAI/Flowise/commit/2f528ceced74afaa95fc7a282965e7788796448b
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
