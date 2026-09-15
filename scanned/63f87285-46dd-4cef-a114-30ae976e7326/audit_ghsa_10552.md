# [H] Arcane Vulnerable to Unauthenticated Disclosure of Custom Compose Template Content (incl. `.env` secrets) 

## Summary
Severity: High
Advisory: GHSA-cxx3-hr75-4q96
CVE: CVE-2026-42461
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-cxx3-hr75-4q96
Type: github-advisory

## Affected
- Go: `github.com/getarcaneapp/arcane/backend` — affected >=0 <1.18.0

## Details
### Summary
Four `GET` endpoints under `/api/templates*` in Arcane's Huma backend are registered without any `Security` requirement, allowing any unauthenticated network client to list and read the full Compose YAML and `.env` content of every custom template stored in the instance. Because Arcane's UI exposes a "Save as Template" flow on the project / swarm-stack creation pages that persists the operator's *real* env content (database passwords, API keys, etc.) verbatim, this missing authorization is an unauthenticated read of operator secrets in practice — not a theoretical info-disclosure.

The frontend explicitly treats `/customize/templates/*` as an authenticated area (`PROTECTED_PREFIXES` in `frontend/src/lib/utils/redirect.util.ts`), and every CRUD operation (POST/PUT/DELETE) on the same paths requires a Bearer/API key, so this is a clear backend authorization gap, not intended public access.

### Details
Affected file: `backend/internal/huma/handlers/templates.go:194-228`.

In `RegisterTemplates`, four `huma.Register` calls have no `Security:` block:

```go
// templates.go
huma.Register(api, huma.Operation{
    OperationID: "listTemplatesPaginated",
    Method:      "GET",
    Path:        "/templates",
    ...
    // <-- no Security
}, h.ListTemplates)

huma.Register(api, huma.Operation{
    OperationID: "getAllTemplates",
    Method:      "GET",
    Path:        "/templates/all",
    ...
}, h.GetAllTemplates)

huma.Register(api, huma.Operation{
    OperationID: "getTemplate",
    Method:      "GET",
    Path:        "/templates/{id}",
    ...
}, h.GetTemplate)

huma.Register(api, huma.Operation{
    OperationID: "getTemplateContent",
    Method:      "GET",
    Path:        "/templates/{id}/content",
    ...
}, h.GetTemplateContent)
```

Arcane's auth bridge (`backend/internal/huma/middleware/auth.go:168-172`) only enforces authentication when the operation declares one of the security schemes (`BearerAuth` or `ApiKeyAuth`). With `Security` omitted, `parseSecurityRequirements` returns `isRequired=false` and the request flows through with no token check.

`TemplateHandler.GetTemplateContent` (`templates.go:478-499`) calls `templateService.GetTemplateContentWithParsedData` (`backend/internal/services/template_service.go:1303-1347`), which returns the model's `Content`, `EnvContent`, parsed services, and parsed env-variable key/value pairs verbatim. The model `models.ComposeTemplate` (`backend/internal/models/template.go:15-16`) stores `Content` and `EnvContent` as plain `text` columns and has no owner / user binding.

### Impact
- Pre-auth confidentiality breach. An unauthenticated client on the same network (or through any path-unaware reverse proxy) recovers the full `envContent` of every locally-stored Compose template. Because the supported "Save as Template" workflow takes the operator's real env values verbatim, this commonly includes database passwords, registry tokens, third-party API keys (Stripe, Sentry, etc.), and OIDC client secrets.
- Internal asset enumeration. `GET /api/templates` returns names, descriptions, tags, and registry metadata for every template, leaking what services the team runs internally and which compose files they reuse

## References
- https://github.com/getarcaneapp/arcane/security/advisories/GHSA-cxx3-hr75-4q96
- https://nvd.nist.gov/vuln/detail/CVE-2026-42461
- https://github.com/getarcaneapp/arcane
- https://github.com/getarcaneapp/arcane/releases/tag/v1.18.0
