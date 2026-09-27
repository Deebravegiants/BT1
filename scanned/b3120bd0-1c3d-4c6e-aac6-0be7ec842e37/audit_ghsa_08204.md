# [M] Open WebUI: Sharing models for others to use (read permission) also exposes model details (system prompt leakage)

## Summary
Severity: Medium
Advisory: GHSA-h2cw-7qw9-56xr
CVE: CVE-2026-45387
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-h2cw-7qw9-56xr
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
### Summary
When setting model permissions so that a group has read access to it, intending for other users to use it, those users also can read the model's system prompt.

However users may consider their system prompt confidential, so we consider this a security issue.

Compare https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/ or prompt injections to get popular chatbots on the internet to reveal their prompt.

### Details

We discovered that users can open the workspace model edit page /workspace/models/edit?id=notmymodel for models that do not appear in their workspace.

Saving is not possible, that permission check is correct.

On the API level:

- ```/api/v1/models/model?id=notmymodel``` -> returns the model details, most importantly params.system
- even though ```/api/v1/models/list``` does NOT contain the model since it checks for write permission.
- ```/api/models``` contains the model correctly and does not reveal the system prompt.

It seems inconsistent that the REST API list does not contain an item, but if you know the id, you can access it anyway.

### PoC
- create model
- give read permission to group with another user
- other user can access ```/api/v1/models/model?id=notmymodel```

### Impact
System prommpt leakage

If this is intended behavior for the "read" permission, maybe there should be an additional "use" permission (which would be 99% of use cases of the read permission i believe).

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-h2cw-7qw9-56xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45387
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
