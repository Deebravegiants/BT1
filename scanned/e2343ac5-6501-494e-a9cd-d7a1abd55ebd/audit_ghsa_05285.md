# [H] Langflow: IDOR Vulnerability in `/api/v1/responses` Endpoint Allows Authenticated Attackers to Access Another User's Flow

## Summary
Severity: High
Advisory: GHSA-qrpv-q767-xqq2
CVE: CVE-2026-55255
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-qrpv-q767-xqq2
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.1

## Details
## Summary

Insecure Direct Object Reference (IDOR) vulnerability in `/api/v1/responses` endpoint allows an authenticated attacker to execute any flow belonging to another user by specifying the victim's flow ID in the request.

## Details

The vulnerability exists in the `get_flow_by_id_or_endpoint_name` helper function in [`src/backend/base/langflow/helpers/flow.py` (lines 399-414)](https://github.com/langflow-ai/langflow/blob/v1.9.0/src/backend/base/langflow/helpers/flow.py#L399C1-L414C67).

When a flow is accessed via UUID (flow_id), the function queries the database directly without verifying if the authenticated user owns that flow:

```python
# src/backend/base/langflow/helpers/flow.py:399-414
async def get_flow_by_id_or_endpoint_name(flow_id_or_name: str, user_id: str | UUID | None = None) -> FlowRead:
    async with session_scope() as session:
        try:
            flow_id = UUID(flow_id_or_name)
            # When using UUID, query directly WITHOUT checking user_id
            flow = await session.get(Flow, flow_id)  # ❌ No user_id check!
        except ValueError:
            endpoint_name = flow_id_or_name
            stmt = select(Flow).where(Flow.endpoint_name == endpoint_name)
            # Only when using endpoint_name is user_id checked
            if user_id:
                stmt = stmt.where(Flow.user_id == uuid_user_id)
```

This function is used by the `/api/v1/responses` endpoint (defined in [`src/backend/base/langflow/api/v1/openai_responses.py:589`](https://github.com/langflow-ai/langflow/blob/v1.9.0/src/backend/base/langflow/api/v1/openai_responses.py#L589)).

## PoC (Proof of Concept)

```bash
# Attacker (user A) with API_KEY_A tries to execute victim (user B)'s flow
curl -X POST "http://localhost:7860/api/v1/responses" \
  -H "x-api-key: sk-ATTACKER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "VICTIM_FLOW_ID",
    "input_value": "test",
    "stream": false
  }'
# Returns 200 and executes the victim's flow
```

## Impact

Any authenticated user can:
1. Execute any flow in the system by knowing its flow ID
2. Access potentially sensitive data processed by victim's flows
3. Consume victim's resources

## Fixes

Fixed in **PR #12832** (`fix(security): close IDOR in get_flow_by_id_or_endpoint_name`), merged 2026-04-22, released in **Langflow 1.9.1**.

The helper normalizes `user_id` once and enforces ownership on **both** lookup branches (UUID *and* `endpoint_name`):

```python
flow_id = UUID(flow_id_or_name)
flow = await session.get(Flow, flow_id)
if flow is not None and uuid_user_id is not None and flow.user_id != uuid_user_id:
    flow = None  # cross-user lookup falls through to the shared 404
```

Key points:
- Cross-user lookups return **404** (not 403), so flow existence is not disclosed via a 403-vs-404 oracle.
- `/api/v1/responses` and `/api/v2/workflow` pass `user_id` explicitly, so fixing the helper closes them directly; the `/api/v1/run*` routes were additionally moved from a bare `Depends(get_flow_by_id_or_endpoint_name)` to auth-aware wrapper dependencies (defense in depth).
- A malformed `user_id` now fails closed (404 instead of a raw 500).
- Webhook routes intentionally keep the unscoped lookup (public by design / explicit ownership check elsewhere).
- Regression tests cover the cross-user UUID case and reproduce the original PoC against `/api/v1/responses`.





## Acknowledgements

Thanks to the security researchers who responsibly disclosed this vulnerability:
* @yzeirnials
* @johnatzeropath
* @LeftenantZero
* @Zwique

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-qrpv-q767-xqq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-55255
- https://github.com/langflow-ai/langflow/pull/12832
- https://github.com/langflow-ai/langflow/commit/2c9f498d664a3c32698b57d7c5e752625291060e
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-221.yaml
- https://webflow.sysdig.com/blog/understanding-langflow-cve-2026-55255-and-why-higher-cvss-vulnerabilities-arent-always-the-most-exploited
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-55255
