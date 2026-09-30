# [M] Portainer missing authorization on custom template file endpoint, which exposes template content

## Summary
Severity: Medium
Advisory: GHSA-cqpq-2fgr-8mvc
CVE: CVE-2026-44884
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-cqpq-2fgr-8mvc
Type: github-advisory

## Affected
- Go: `github.com/portainer/portainer` — affected >=2.33.0 <2.33.8
- Go: `github.com/portainer/portainer` — affected >=2.39.0 <2.39.1

## Details
## Summary
A missing authorization vulnerability in the Custom Template file endpoint (`GET /api/custom_templates/{id}/file`) allows any authenticated user to read the file content of any custom template by enumerating sequential integer IDs, bypassing Resource Control access restrictions. Template files may contain environment-specific values such as connection strings, API tokens, or registry credentials that administrators would not expect standard users to read.

## Severity

**Medium**

**CWE-862** — Missing Authorization

Exploitation requires an authenticated user account and at least one custom template to exist. Template files are returned verbatim and may contain embedded credentials.

## Affected Versions

The vulnerability exists in every Portainer release since custom templates were introduced — the `customTemplateFile` handler has never performed an authorization check.

Fixes are included in the following releases:

| Branch              | First vulnerable | Fixed in   |
|---------------------|------------------|------------|
| 2.33.x (LTS)        | 2.33.0           | **2.33.8** |
| 2.39.x (LTS)        | 2.39.0           | **2.39.1** |

Portainer 2.40.0 and later are not affected — the fix was already on `develop` when the 2.40.x STS line branched. Portainer LTS branches receive fixes for 6 months plus a 3-month overlap after the next LTS ships. All releases **prior to 2.33.0 are end-of-life** and will not receive a fix; users on EOL versions should upgrade to a supported release.

## Workarounds

There is no runtime configuration that blocks the vulnerable endpoint directly. Administrators who cannot immediately upgrade can reduce exposure by:

- **Avoiding storing secrets in custom templates** until the patched release is deployed. Move sensitive configuration values to Portainer environment variables or an external secret store.
- **Reviewing existing custom templates** for embedded secrets. Assume any secret previously stored in a custom template on an unpatched instance has been exposed to every authenticated user and rotate accordingly.

Neither replaces the fix.

## Affected Code
The `customTemplateFile` handler in `api/http/handler/customtemplates/customtemplate_file.go` (lines 30-53) retrieves a custom template by its numeric ID and returns the file content without performing any authorization check.

All other custom template endpoints properly verify access:

| Endpoint | Method | Authorization Check |
|----------|--------|-------------------|
| `/api/custom_templates/{id}` | GET (inspect) | `userCanEditTemplate()` + `UserCanAccessResource()` |
| `/api/custom_templates/{id}` | PUT (update) | `userCanEditTemplate()` |
| `/api/custom_templates/{id}` | DELETE | `userCanEditTemplate()` |
| `/api/custom_templates` | GET (list) | `FilterAuthorizedCustomTemplates()` |
| **`/api/custom_templates/{id}/file`** | **GET** | **None** |

**Vulnerable code** (`customtemplate_file.go:30-53`):
```go
func (handler *Handler) customTemplateFile(w http.ResponseWriter, r *http.Request) *httperror.HandlerError {
    customTemplateID, _ := request.RetrieveNumericRouteVariableValue(r, "id")
    customTemplate, _ := handler.DataStore.CustomTemplate().Read(portainer.CustomTemplateID(customTemplateID))
    // NO AUTHORIZATION CHECK
    fileContent, _ := handler.FileService.GetFileContent(customTemplate.ProjectPath, entryPath)
    return response.JSON(w, &fileResponse{FileContent: string(fileContent)})
}
```

**Secure reference** (`customtemplate_inspect.go:50-75`):
```go
canEdit := userCanEditTemplate(customTemplate, securityContext)
hasAccess := authorization.UserCanAccessResource(securityContext.UserID, teamIDs, resourceControl)
if !canEdit && !hasAccess {
    return httperror.Forbidden("Access denied to resource", httperrors.ErrResourceAccessDenied)
}
```

## Impact
Any authenticated user (including the lowest-privilege standard user) can read the file content of every custom template in the instance. Custom templates commonly contain Docker Compose configuration, which may include environment-specific secrets such as database connection strings, API tokens, or registry credentials.

## Timeline

- 2026-02-11: Reported via GitHub Security Advisory by **duddnr0615k**.
- 2026-03-04: Fix merged to `develop` and cherry-picked to `release/2.39`.
- 2026-03-19: 2.39.1 released with fix.
- 2026-03-25: 2.40.0 released with fix already present from branch cut.
- 2026-05-07: 2.33.8 released.

## Credit

- **duddnr0615k** — identified and reported the missing authorization check on the custom template file endpoint.

## References
- https://github.com/portainer/portainer/security/advisories/GHSA-cqpq-2fgr-8mvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44884
- https://github.com/portainer/portainer
- https://github.com/portainer/portainer/releases/tag/2.33.8
- https://github.com/portainer/portainer/releases/tag/2.39.2
