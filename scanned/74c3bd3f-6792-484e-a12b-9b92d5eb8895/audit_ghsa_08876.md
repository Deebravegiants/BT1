# [H] Arcane: Missing admin authorization on global variables endpoint

## Summary
Severity: High
Advisory: GHSA-jpjh-jm2p-39hh
CVE: CVE-2026-47125
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-23
Source: https://github.com/advisories/GHSA-jpjh-jm2p-39hh
Type: github-advisory

## Affected
- Go: `github.com/getarcaneapp/arcane/backend` — affected >=0 <1.19.2

## Details
## Summary

The `PUT /api/environments/{id}/templates/variables` endpoint, which writes the system-wide `.env.global` file used for variable substitution in every project's compose file, is missing an admin authorization check. Any authenticated non-admin user can call this endpoint with their bearer token or API key and overwrite the global environment variables that are merged into every project deployment. By overriding values like `REGISTRY`, `IMAGE`, `DATABASE_URL`, or `SECRET_KEY` that other users reference via `${VAR}` in compose files, an attacker can redirect image pulls to attacker-controlled registries (supply-chain RCE on the Docker host), exfiltrate database credentials, or disrupt all projects.

## Details

The endpoint is registered at `backend/internal/huma/handlers/templates.go:374`:

```go
huma.Register(api, huma.Operation{
    OperationID: "updateGlobalVariables",
    Method:      "PUT",
    Path:        "/environments/{id}/templates/variables",
    ...
    Security: []map[string][]string{
        {"BearerAuth": {}},
        {"ApiKeyAuth": {}},
    },
}, h.UpdateGlobalVariables)
```

The handler at `backend/internal/huma/handlers/templates.go:889` performs no role check:

```go
func (h *TemplateHandler) UpdateGlobalVariables(ctx context.Context, input *UpdateGlobalVariablesInput) (*UpdateGlobalVariablesOutput, error) {
    if h.templateService == nil {
        return nil, huma.Error500InternalServerError("service not available")
    }

    if input.EnvironmentID != "0" {
        return h.updateGlobalVariablesForRemoteEnvironmentInternal(ctx, input)
    }

    if err := h.templateService.UpdateGlobalVariables(ctx, input.Body.Variables); err != nil {
        return nil, huma.Error500InternalServerError((&common.GlobalVariablesUpdateError{Err: err}).Error())
    }
    ...
}
```

This is anomalous compared to every other admin-sensitive handler in the codebase, all of which begin with `if err := checkAdmin(ctx); err != nil { return nil, err }` (see `users.go`, `events.go`, `swarm.go`, `settings.go`, `apikeys.go`, `environments.go`, `notifications.go`, `container_registries.go`, `git_repositories.go`, `system.go`). The helper exists at `backend/internal/huma/handlers/helpers.go:12` but is never invoked from `templates.go`.

The auth middleware at `backend/internal/huma/middleware/auth.go:192-254` only validates that *some* authenticated user is present (Bearer JWT, API key, or environment access token); it does not enforce roles. Role enforcement is the responsibility of each handler.

That this endpoint is intended to be admin-only is evidenced by the UI customization search at `backend/internal/huma/handlers/customize.go:82-91` and `:106-114`, which explicitly hides the `variables` and `registries` categories from non-admin users:

```go
if !humamw.IsAdminFromContext(ctx) {
    filtered := []category.Category{}
    for _, cat := range results.Results {
        if cat.ID != "registries" && cat.ID != "variables" {
            filtered = append(filtered, cat)
        }
    }
    results.Results = filtered
    ...
}
```

The corresponding `container_registries.go` handlers all enforce admin via `checkAdmin()` (e.g. `container_registries.go:273,329,360,387,442`); the equivalent enforcement for the global-variables write was forgotten.

The service layer at `backend/internal/services/template_service.go:1107` writes attacker-supplied keys/values to `<projectsDirectory>/.env.global`:

```go
func (s *TemplateService) UpdateGlobalVariables(ctx context.Context, vars []env.Variable) error {
    envPath, err := s.getGlobalVariablesPath(ctx)
    ...
    for _, v := range vars {
        if strings.TrimSpace(v.Key) == "" { continue }
        key := strings.TrimSpace(v.Key)
        value := strings.TrimSpace(v.Value)
        if strings.ContainsAny(value, " \t\n\r#") {
            value = fmt.Sprintf(`"%s"`, strings.ReplaceAll(value, `"`, `\"`))
        }
        _, _ = fmt.Fprintf(&builder, "%s=%s\n", key, value)
    }
    if err := projects.WriteFileWithPerm(envPath, builder.String(), common.FilePerm); err != nil { ... }
}
```

That file is then loaded for every project at deploy time via `backend/pkg/projects/env.go:65-82` (`EnvLoader.LoadEnvironment` → `loadAndMergeGlobalEnv`):

```go
if strings.TrimSpace(l.projectsDir) != "" {
    globalEnvPath := filepath.Join(l.projectsDir, GlobalEnvFileName)
    if err := l.loadAndMergeGlobalEnv(ctx, globalEnvPath, envMap, injectionVars); err != nil ...
}
```

`loadAndMergeGlobalEnv` (`env.go:94-125`) populates both `envMap` (used by compose-go for `${VAR}` substitution in compose files) and `injectionVars` (auto-injected into containers). The result: a single non-admin write to the global variables endpoint changes the resolved compose state of every project on the host.

Additionally, the key field is only `strings.TrimSpace`'d (`template_service.go:1128`); embedded newlines inside the key are not removed, so a key like `"FOO\nINJECTED"` will write two lines into `.env.global`, allowing arbitrary key injection and overwrite of variables an attacker did not include in their request body.

## Impact

- **Cross-project supply-chain RCE on the Docker host.** Compose files commonly reference `${REGISTRY}/${IMAGE}:${TAG}`. By pointing `REGISTRY` (or `IMAGE`) at an attacker-controlled registry, the next deploy of any affected project pulls and runs attacker code with whatever privileges Arcane gives that container (commonly Docker socket access, host volume mounts, etc.).
- **Credential theft from other users' projects.** Variables like `DATABASE_URL`, `SMTP_HOST`, `WEBHOOK_URL`, `S3_ENDPOINT` can be redirected to attacker-controlled servers; the next deploy will hand the new connection strings to applications that then submit credentials/data to the attacker.
- **Cross-tenant integrity and availability.** A single non-admin user can corrupt `.env.global` to break every project on the instance.
- **Bypass of intended privilege boundary.** The UI explicitly hides the variables and registries surfaces from non-admins, indicating these are admin-only controls; this finding closes the gap between the documented privilege model and the API enforcement.

The privilege delta is significant: the project clearly distinguishes admin from non-admin users (separate roles, admin-only UI categories, `checkAdmin()` enforced on dozens of other endpoints), yet this endpoint grants a non-admin the ability to execute attacker-controlled images on the host on behalf of every other tenant.

## References
- https://github.com/getarcaneapp/arcane/security/advisories/GHSA-jpjh-jm2p-39hh
- https://nvd.nist.gov/vuln/detail/CVE-2026-47125
- https://github.com/getarcaneapp/arcane
