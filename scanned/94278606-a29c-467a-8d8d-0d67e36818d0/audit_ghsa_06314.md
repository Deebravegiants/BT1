# [M] Pydantic AI: Unvalidated UploadedFile references in UI adapters allow server-side file access using the application's credentials

## Summary
Severity: Medium
Advisory: GHSA-h7p7-w5gc-xj3w
CVE: CVE-2026-54249
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-h7p7-w5gc-xj3w
Type: github-advisory

## Affected
- PyPI: `pydantic-ai-slim` — affected >=1.65.0 <1.106.0
- PyPI: `pydantic-ai-slim` — affected >=2.0.0b1 <2.0.0b6
- PyPI: `pydantic-ai` — affected >=1.65.0 <1.106.0
- PyPI: `pydantic-ai` — affected >=2.0.0b1 <2.0.0b6

## Details
### Summary

A client that can submit message history to a Pydantic AI UI adapter can reference arbitrary files in the application's model-provider or cloud-storage account. The server forwards the reference to the model provider, which fetches it using the server's own credentials, allowing the client to read files it should not have access to.

### Details

UI adapters reconstruct file parts from client-submitted message history and forward them to the model provider. File **URL** parts are validated against a scheme allowlist before being forwarded, but `UploadedFile` references — which point to a file by provider file ID or cloud-storage URI (e.g. `s3://…`, `gs://…`) — were forwarded without validation.

Because the provider resolves an `UploadedFile` using the server-side identity (IAM role, service account, or provider API key) rather than the client's, a client that crafts message history containing an attacker-chosen `UploadedFile` can cause the server to read objects belonging to its own account or to other tenants, given a referenceable identifier.

### Impact

Applications that pass untrusted client-submitted message history to an agent through a UI adapter (such as the Vercel AI adapter). Exploitation requires the attacker to reference a valid file identifier; depending on how the application names objects, such identifiers are not always unguessable.

### Patches

Upgrade to `1.106.0` (1.x) or `2.0.0b6` (the 2.x beta line), which validate `UploadedFile` references on client-submitted messages the same way file URLs are validated.

### Workarounds

If users cannot upgrade, do not pass untrusted client-submitted message history to the agent, or strip `UploadedFile` parts from incoming messages before running the agent.

## References
- https://github.com/pydantic/pydantic-ai/security/advisories/GHSA-h7p7-w5gc-xj3w
- https://nvd.nist.gov/vuln/detail/CVE-2026-54249
- https://github.com/pydantic/pydantic-ai
- https://github.com/pydantic/pydantic-ai/releases/tag/v1.106.0
- https://github.com/pydantic/pydantic-ai/releases/tag/v2.0.0b6
