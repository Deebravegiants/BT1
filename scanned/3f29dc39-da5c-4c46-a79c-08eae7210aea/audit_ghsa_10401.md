# [H] Flowise: Mass Assignment in DocumentStore Create Endpoint Leads to Cross-Workspace Object Takeover (IDOR)

## Summary
Severity: High
Advisory: GHSA-3prp-9gf7-4rxx
CVE: CVE-2026-41277
CWE: CWE-284, CWE-639, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-3prp-9gf7-4rxx
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
### Summary
A Mass Assignment vulnerability in the DocumentStore creation endpoint allows authenticated users to control the primary key (id) and internal state fields of DocumentStore entities.

Because the service uses repository.save() with a client-supplied primary key, the POST create endpoint behaves as an implicit UPSERT operation. This enables overwriting existing DocumentStore objects.

In multi-workspace or multi-tenant deployments, this can lead to cross-workspace object takeover and broken object-level authorization (IDOR), allowing an attacker to reassign or modify DocumentStore objects belonging to other workspaces.

### Details
The DocumentStore entity defines a globally unique primary key:

```typescript
@PrimaryGeneratedColumn('uuid')
id: string
```

The create logic is implemented as:
```typescript
const documentStore = repo.create(newDocumentStore)
const dbResponse = await repo.save(documentStore)
```

Here is no DTO allowlist or field filtering before persistence. The entire request body is mapped directly to the entity.
TypeORM save() behavior:

1. If the primary key (id) exists → UPDATE
2. If not → INSERT

Because id is accepted from the client, the create endpoint effectively functions as an UPSERT endpoint.

This allows an authenticated user to submit:

```json
{
  "id": "<existing_store_id>",
  "name": "modified",
  "description": "modified",
  "status": "SYNC",
  "embeddingConfig": "...",
  "vectorStoreConfig": "...",
  "recordManagerConfig": "..."
}
```
If a DocumentStore with the supplied id already exists, save() performs an UPDATE rather than creating a new record.

Importantly:

The primary key is globally unique (uuid)
It is not composite with workspaceId
The create path does not enforce ownership validation before calling save()
This introduces a broken object-level authorization risk.

If an attacker can obtain or enumerate a valid DocumentStore UUID belonging to another workspace, they can:
Submit a POST create request with that UUID.
Trigger an UPDATE on the existing record.
Potentially overwrite fields including workspaceId, effectively reassigning the object to their own workspace.

Because the service layer does not verify that the existing record belongs to the caller’s workspace before updating, this may result in cross-workspace object takeover.

Additionally, several service functions retrieve DocumentStore entities by id without consistently scoping by workspaceId, increasing the risk of IDOR if controller-level protections are bypassed or misconfigured.

### PoC

1. Create a normal DocumentStore in Workspace A.
2. Capture its id from the API response.
3. From Workspace B (or another authenticated context), submit:

```http
POST /api/v1/document-store
Content-Type: application/json

{
  "id": "<id_from_workspace_A>",
  "name": "hijacked",
  "description": "hijacked"
}
```

Because the service uses repository.save() with a client-supplied primary key:

- The existing record is updated.
- The object may become reassigned depending on how workspaceId is handled at controller level.
- If workspaceId is overwritten during the create flow, the store is effectively migrated to the attacker’s workspace.
- This demonstrates object takeover via UPSERT semantics on a create endpoint.

### Impact
This vulnerability enables:

- Mass Assignment on server-managed fields
- Overwrite of existing objects via implicit UPSERT behavior
- Broken Object Level Authorization (BOLA)
- Potential cross-workspace object takeover in multi-tenant deployments
- In a SaaS or shared-workspace environment, an attacker who can obtain or guess a valid UUID may modify or reassign DocumentStore objects belonging to other tenants.

Because DocumentStore objects control embedding providers, vector store configuration, and record management logic, successful takeover can affect data indexing, retrieval, and AI workflow execution.

This represents a high-risk authorization flaw in multi-tenant environments.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-3prp-9gf7-4rxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-41277
- https://github.com/FlowiseAI/Flowise
