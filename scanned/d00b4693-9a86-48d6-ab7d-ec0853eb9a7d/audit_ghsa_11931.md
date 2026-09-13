# [H] Langflow is Missing Ownership Verification in API Key Deletion (IDOR)

## Summary
Severity: High
Advisory: GHSA-rf6x-r45m-xv3w
CVE: CVE-2026-33053
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-rf6x-r45m-xv3w
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.0

## Details
**Detection Method:** Kolega.dev Deep Code Scan

| Attribute | Value |
|---|---|
| Location | src/backend/base/langflow/api/v1/api_key.py:44-53 |
| Practical Exploitability | High |
| Developer Approver | faizan@kolega.ai |

### Description
The delete_api_key_route() endpoint accepts an api_key_id path parameter and deletes it with only a generic authentication check (get_current_active_user dependency). However, the delete_api_key() CRUD function does NOT verify that the API key belongs to the current user before deletion.

### Affected Code
```
@router.delete("/{api_key_id}", dependencies=[Depends(auth_utils.get_current_active_user)])
async def delete_api_key_route(
    api_key_id: UUID,
    db: DbSession,
):
    try:
        await delete_api_key(db, api_key_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"detail": "API Key deleted"}
```

### Evidence
In crud.py lines 44-49, delete_api_key() retrieves the API key by ID and deletes it without checking if the key belongs to the authenticated user. The endpoint also doesn't pass the current_user to the delete function for verification.

### Impact
An authenticated attacker can enumerate and delete API keys belonging to other users by guessing or discovering their API key IDs. This allows account takeover, denial of service, and disruption of other users' integrations.

### Recommendation
Modify the delete_api_key endpoint and function: (1) Pass current_user to the delete function; (2) In delete_api_key(), verify api_key.user_id == current_user.id before deletion; (3) Raise a 403 Forbidden error if the user doesn't own the key. Example: if api_key.user_id != user_id: raise HTTPException(status_code=403, detail='Unauthorized')

### Notes
Confirmed IDOR vulnerability. The delete_api_key_route endpoint at line 44-53 accepts an api_key_id and calls delete_api_key(db, api_key_id) without passing the current_user. The CRUD function delete_api_key() at crud.py:44-49 retrieves the API key by ID and deletes it without verifying ownership (api_key.user_id == current_user.id). Compare this to the GET endpoint at lines 17-28 which correctly filters by user_id, and the POST endpoint at lines 31-41 which correctly associates the key with user_id. An authenticated attacker can delete any user's API keys by guessing/enumerating UUIDs. Fix: Pass current_user to delete_api_key and verify api_key.user_id == current_user.id before deletion, returning 403 if unauthorized.

### Developer Review Notes
Does not accept current_user as a parameter. Allowing deletion of any user's API keys even without permissions.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-rf6x-r45m-xv3w
- https://github.com/langflow-ai/langflow/commit/fdc1b3b1448ff3317d73d3e769a6c4a1717f74d7
- https://github.com/langflow-ai/langflow
- https://github.com/langflow-ai/langflow/releases/tag/1.7.2
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-78.yaml
