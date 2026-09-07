# [M] New API: IDOR in VideoProxy allows cross-user video content access via missing ownership check 

## Summary
Severity: Medium
Advisory: GHSA-f35r-v9x5-r8mc
CVE: CVE-2026-30886
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-f35r-v9x5-r8mc
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <0.11.4-alpha.2

## Details
## Summary

The video proxy endpoint `GET /v1/videos/:task_id/content` is vulnerable to an Insecure Direct Object Reference (IDOR). Any authenticated user who knows another user's `task_id` can retrieve that user's generated video content because the handler queries tasks by `task_id` alone and does not verify ownership.

## Affected Component

- Endpoint: `GET /v1/videos/:task_id/content`
- Route middleware: `TokenOrUserAuth()`
- Vulnerable handler: `controller.VideoProxy`

## Details

`VideoProxy` fetches the task with:

```go
task, exists, err := model.GetByOnlyTaskId(taskID)
```

`GetByOnlyTaskId` performs a database lookup using only `task_id`:

```go
err = DB.Where("task_id = ?", taskId).First(&task).Error
```

The authenticated user's ID is available in request context, but `VideoProxy` does not use it. This allows any authenticated user to request `/v1/videos/<foreign_task_id>/content` and access another user's video if they know a valid task ID.

Other task-fetch paths already enforce ownership correctly via:

```go
model.GetByTaskId(userId, taskId)
```

## Impact

An authenticated attacker who knows another user's `task_id` can:

- Download video content belonging to another user
- Bypass tenant isolation for generated media assets
- Cause the server to fetch upstream video content for a task the attacker does not own

For Gemini tasks, the proxy also uses `task.PrivateData.Key` when contacting the upstream provider. In addition, full upstream response headers are forwarded back to the requester.

## Proof of Concept

```bash
curl -o stolen_video.mp4 \
  "https://<instance>/v1/videos/<victim_task_id>/content" \
  -H "Authorization: Bearer sk-<attacker_token>"
```

Expected result:

- Response returns `200 OK`
- Response body contains the victim's video content

## Recommended Fix

Replace the task lookup in `VideoProxy` with an ownership-checked query:

```go
userId := c.GetInt("id")
task, exists, err := model.GetByTaskId(userId, taskID)
```

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-f35r-v9x5-r8mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-30886
- https://github.com/QuantumNous/new-api/commit/50ec2bac6b341e651fc9ac4344e3bd2cdaeafdbd
- https://github.com/QuantumNous/new-api
