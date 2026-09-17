# [M] WeKnora has Unauthorized Cross‑Tenant Knowledge Base Cloning

## Summary
Severity: Medium
Advisory: GHSA-8rf9-c59g-f82f
CVE: CVE-2026-30857
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-8rf9-c59g-f82f
Type: github-advisory

## Affected
- Go: `github.com/Tencent/WeKnora` — affected >=0 <0.3.0

## Details
### Summary
A cross-tenant authorization bypass in the knowledge base copy endpoint allows any authenticated user to clone (duplicate) another tenant’s knowledge base into their own tenant by knowing/guessing the source knowledge base ID. This enables bulk data exfiltration (document/FAQ content) across tenants, making the impact critical.

### Details

The `POST /api/v1/knowledge-bases/copy` endpoint enqueues an asynchronous KB clone task using the caller-supplied `source_id` without verifying ownership (see `internal/handler/knowledgebase.go`).
```go
// Create KB clone payload
payload := types.KBClonePayload{
  TenantID: tenantID.(uint64),
  TaskID:   taskID,
  SourceID: req.SourceID, // from attacker's input
  TargetID: req.TargetID,
}

payloadBytes, err := json.Marshal(payload)
if err != nil {
  logger.Errorf(ctx, "Failed to marshal KB clone payload: %v", err)
  c.Error(errors.NewInternalServerError("Failed to create task"))
  return
}

// Enqueue KB clone task to Asynq
task := asynq.NewTask(types.TypeKBClone, payloadBytes,
asynq.TaskID(taskID), asynq.Queue("default"), asynq.MaxRetry(3)) // enqueue task
info, err := h.asynqClient.Enqueue(task)
if err != nil {
  logger.Errorf(ctx, "Failed to enqueue KB clone task: %v", err)
  c.Error(errors.NewInternalServerError("Failed to enqueue task"))
  return
}
```

Then, the asynq task handler (`ProcessKBClone`) invokes the `CopyKnowledgeBase` service method to perform the clone operation (see `internal/application/service/knowledge.go`):

```go
// Get source and target knowledge bases
srcKB, dstKB, err := s.kbService.CopyKnowledgeBase(ctx, payload.SourceID, payload.TargetID)
if err != nil {
    logger.Errorf(ctx, "Failed to copy knowledge base: %v", err)
    handleError(progress, err, "Failed to copy knowledge base configuration")
    return err
}
```

After that, the `CopyKnowledgeBase` method calls the repository method to load the source knowledge base (see `internal/application/service/knowledgebase.go`):

```go
func (s *knowledgeBaseService) CopyKnowledgeBase(ctx context.Context,
	srcKB string, dstKB string,
) (*types.KnowledgeBase, *types.KnowledgeBase, error) {
	sourceKB, err := s.repo.GetKnowledgeBaseByID(ctx, srcKB)
	if err != nil {
		logger.Errorf(ctx, "Get source knowledge base failed: %v", err)
		return nil, nil, err
	}
	sourceKB.EnsureDefaults()
	tenantID := ctx.Value(types.TenantIDContextKey).(uint64)
	var targetKB *types.KnowledgeBase
	if dstKB != "" {
		targetKB, err = s.repo.GetKnowledgeBaseByID(ctx, dstKB)
        // ...
    }
    // ...
}
```


> Note: until now, the tenant ID is correctly set in context to the attacker’s tenant (from the payload), which can be used to prevent cross-tenant access.

However, the repository method `GetKnowledgeBaseByID` loads knowledge bases by `id` only, allowing cross-tenant reads (see `internal/application/repository/knowledgebase.go`).

```go
func (r *knowledgeBaseRepository) GetKnowledgeBaseByID(ctx context.Context, id string) (*types.KnowledgeBase, error) {
	var kb types.KnowledgeBase
	if err := r.db.WithContext(ctx).Where("id = ?", id).First(&kb).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrKnowledgeBaseNotFound
		}
		return nil, err
	}
	return &kb, nil
}
```

The data access layer fails to enforce tenant isolation because `GetKnowledgeBaseByID` only filters by ID and ignores the `tenant_id` present in the context. A secure implementation should enforce a tenant-scoped lookup (e.g., `WHERE id = ? AND tenant_id = ?`) or use a tenant-aware repository API to prevent cross-tenant access.

Service shallow-copies the KB configuration by calling `GetKnowledgeBaseByID(ctx, srcKB)` for the source KB, then creates a new KB under the attacker’s tenant while copying fields from the victim KB (`internal/application/service/knowledgebase.go`):

```go
sourceKB, err := s.repo.GetKnowledgeBaseByID(ctx, srcKB) // not tenant-scoped
...
targetKB = &types.KnowledgeBase{
    ID:                    uuid.New().String(),
    Name:                  sourceKB.Name,
    Type:                  sourceKB.Type,
    Description:           sourceKB.Description,
    TenantID:              tenantID,
    ChunkingConfig:        sourceKB.ChunkingConfig,
    ImageProcessingConfig: sourceKB.ImageProcessingConfig,
    EmbeddingModelID:      sourceKB.EmbeddingModelID,
    SummaryModelID:        sourceKB.SummaryModelID,
    VLMConfig:             sourceKB.VLMConfig,
    StorageConfig:         sourceKB.StorageConfig,
    FAQConfig:             faqConfig,
}
targetKB.EnsureDefaults()
  if err := s.repo.CreateKnowledgeBase(ctx, targetKB); err != nil {
      return nil, nil, err
  }
}
```

### PoC

Precondition: Attacker is authenticated in Tenant A and can obtain (or guess) a victim's knowledge base UUID belonging to Tenant B.

1) Authenticate as Tenant A and obtain a bearer token or API key.

2) Start a cross-tenant clone using the victim’s knowledge base ID as `source_id`:

```bash
curl -X POST http://localhost:8088/api/v1/knowledge-bases/copy \
  -H "Authorization: Bearer <ATTACKER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"source_id":"<VICTIM_KB_UUID>","target_id":""}'
```

3) Observe that the task is accepted:
- HTTP `200 OK`
- Response contains a `task_id` and a message like `"Knowledge base copy task started"`.

4) After the async task completes, a new knowledge base appears under Tenant A containing copied content/config from Tenant B.

> Note: the copy can succeed even when models referenced by the source KB do not exist in the attacker tenant, indicating the workflow does not validate model ownership during copy.

PoC Video:

https://github.com/user-attachments/assets/8313fa44-5d5d-43f4-8ebd-f465c5a9d56e

### Impact

This is a Broken Access Control (BOLA/IDOR) vulnerability enabling cross-tenant data exfiltration:

- Any authenticated user can trigger a clone of a victim tenant’s knowledge base into their own tenant.
- Results in bulk disclosure/duplication of knowledge base contents (documents/FAQ entries/chunks), plus associated configuration.

## References
- https://github.com/Tencent/WeKnora/security/advisories/GHSA-8rf9-c59g-f82f
- https://nvd.nist.gov/vuln/detail/CVE-2026-30857
- https://github.com/Tencent/WeKnora
