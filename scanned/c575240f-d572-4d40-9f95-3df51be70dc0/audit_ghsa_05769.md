# [H] Flowise: Cross-workspace credential IDOR in openai-assistants-vector-store

## Summary
Severity: High
Advisory: GHSA-chm3-vqcf-52rx
CVE: CVE-2026-70472
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:H/SA:H (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-chm3-vqcf-52rx
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
# Summary 

These endpoints accept a client-controlled `credential` parameter. The server loads credentials by `id` and uses them directly, without checking whether that credential belongs to the caller’s workspace. If an attacker knows another workspace’s `credentialId`, they can use that workspace’s OpenAI key.

# Details

Route permissions (`assistants:*`) only check feature access. They do not check credential ownership. The controller passes `req.query.credential` straight to the service. The service does `findOneBy({ id: credentialId })`, decrypts the credential, and calls OpenAI APIs. There is no `workspaceId` check in this flow, so this is an IDOR.

# Impact 


- Cross-workspace unauthorized use of stored OpenAI keys.
- Unauthorized read/modify/delete of victim vector stores and files.
- Direct billing impact on victim OpenAI account.
- Multi-tenant boundary violation with practical exploitability.

# Reproduction steps  

1. Set up two workspaces: A (attacker) and B (victim), each with an OpenAI credential.  
2. Log in as a user in workspace A (with assistants-related permissions).  
3. Call `/api/v1/openai-assistants-vector-store` and set `credential` to B’s credential ID.  
4. Example: `GET /api/v1/openai-assistants-vector-store?credential=<B_credentialId>`.  
5. If responses/actions are executed using B’s credential context, the issue is confirmed.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-chm3-vqcf-52rx
- https://github.com/FlowiseAI/Flowise/pull/6170
- https://github.com/FlowiseAI/Flowise/commit/d81483b70c997ddf981acc9c49fbd9a02fa345cd
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
