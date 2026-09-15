# [H] FlowiseAI has Mass Assignment in Chatflow Update Endpoint that Allows Cross-Workspace AgentFlow Reassignment

## Summary
Severity: High
Advisory: GHSA-5wxp-qjgq-fx6m
CVE: CVE-2026-42863
CWE: CWE-284, CWE-639, CWE-915
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-5wxp-qjgq-fx6m
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
### Summary
A Mass Assignment vulnerability exists in the chatflow update endpoint of FlowiseAI.

The endpoint allows clients to modify server-controlled properties such as deployed, isPublic, workspaceId, createdDate, and updatedDate when updating a chatflow object.

Due to missing server-side validation and authorization checks, an authenticated user can manipulate internal attributes of a chatflow and reassign it to another workspace. This allows cross-workspace resource reassignment and unauthorized modification of deployment and visibility settings.

### Details
The endpoint responsible for updating chatflows:

**PUT /api/v1/chatflows/{chatflowId}**

accepts a JSON request body containing the chatflow configuration (flowData) along with other metadata fields.

However, the server does not restrict which properties may be modified by the client. As a result, user-controlled request bodies can include additional fields that should normally be controlled only by the backend.

Examples of server-controlled fields that can be manipulated include:

1. deployed
2. isPublic
3. workspaceId
4. createdDate
5. updatedDate
6. category
7. type

These fields appear to be directly mapped to the underlying database entity when processing the update request, suggesting that the server performs a direct merge of the request body into the chatflow model without applying a strict DTO whitelist or authorization checks.

For example, modifying the request body with:

```json
{
  "deployed": true,
  "isPublic": true,
  "createdDate": "1999-03-06T10:59:32.000Z",
  "updatedDate": "1999-03-06T13:21:34.000Z",
  "workspaceId": "11111111-2222-3333-4444-555555555555"
}
```

results in the server accepting and persisting these values.

In testing, a second workspace was created in the database and the workspaceId field was successfully modified through the API request. The chatflow was reassigned to the attacker-controlled workspace, confirming that the application does not enforce workspace ownership validation.


### PoC
Authenticate to the Flowise interface.

Capture the request used to update a chatflow:

```http
PUT /api/v1/chatflows/<CHATFLOW_ID>
Content-Type: application/json

Modify the request body by injecting additional fields:

{
  "name": "test-flow",
  "flowData": "{...}",
  "deployed": true,
  "isPublic": true,
  "workspaceId": "11111111-2222-3333-4444-555555555555"
}
```

Send the request.

Observe that the response returns the manipulated values:

```json
{
  "deployed": true,
  "isPublic": true,
  "workspaceId": "11111111-2222-3333-4444-555555555555"
}
```

Verify in the database that the chatflow has been reassigned:

```sql
SELECT id, workspaceId FROM chat_flow WHERE id='<CHATFLOW_ID>';
```

The workspaceId value reflects the attacker-supplied workspace.

### Impact
This vulnerability allows authenticated users to manipulate server-controlled attributes of chatflows.

Confirmed impacts include:

- Unauthorized modification of chatflow visibility (isPublic)
- Unauthorized deployment state changes (deployed)
- Cross-workspace reassignment of chatflows (workspaceId)
- Unauthorized modification of metadata (createdDate, updatedDate)

In multi-tenant environments, this allows an attacker to move chatflows between workspaces without authorization, breaking tenant isolation boundaries.

This may enable:

- Cross-workspace workflow takeover
- Unauthorized exposure of private workflows
- Manipulation of deployed agent workflows

The issue stems from missing authorization checks and improper handling of client-controlled input in the chatflow update endpoint.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-5wxp-qjgq-fx6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-42863
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
