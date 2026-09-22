# [H] Arcane Backend: Unauthenticated reflected XSS via SVG color parameter enables admin account takeover

## Summary
Severity: High
Advisory: GHSA-q2pj-8v84-9mh5
CVE: CVE-2026-45627
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-q2pj-8v84-9mh5
Type: github-advisory

## Affected
- Go: `github.com/getarcaneapp/arcane/backend` — affected >=0 <1.19.0

## Details
## Summary

The unauthenticated `GET /api/app-images/logo` endpoint reflects a user-supplied `color` query parameter into the body of an SVG document via `strings.ReplaceAll` with no escaping. The substitution lands inside a `<style>` element of the embedded `logo.svg`, allowing an attacker to close the style block and inject executable `<script>` content. Because the response is served as `image/svg+xml` and Arcane sets no Content-Security-Policy or `X-Content-Type-Options` headers, navigating a logged-in admin victim to a crafted URL executes attacker-controlled JavaScript in Arcane's origin and rides the victim's HttpOnly JWT cookie to fully compromise the admin account.

## Details

The route is registered in `backend/internal/huma/handlers/appimages.go:53-61` with an explicitly empty security requirement, marking it as public:

```go
huma.Register(api, huma.Operation{
    OperationID: "get-logo",
    Method:      http.MethodGet,
    Path:        "/app-images/logo",
    ...
    Security:    []map[string][]string{}, // explicit: no auth
}, h.GetLogo)
```

`backend/internal/huma/middleware/auth.go:209-213` honors the empty `Security` value by returning `reqs.isRequired == false` and short-circuiting with `next(ctx)`, so no JWT/API-key check runs.

`GetLogoInput.Color` (`appimages.go:23`) is declared with no validation tags:

```go
type GetLogoInput struct {
    Full  bool   `query:"full" default:"false" ...`
    Color string `query:"color" doc:"Optional accent color override ..."`
}
```

The handler passes the value straight through `getImageWithColor` → `ApplicationImagesService.GetImageWithColor` → `applyAccentColorToSVG` (`backend/internal/services/app_images_service.go:79-105`):

```go
svgStr = strings.ReplaceAll(svgStr, "fill:#6D28D9", fmt.Sprintf("fill:%s", accentColor))
svgStr = strings.ReplaceAll(svgStr, "fill:#6d28d9", fmt.Sprintf("fill:%s", accentColor))
```

The bundled `backend/resources/images/logo.svg` contains:

```xml
<style id="style1" type="text/css">.st0{fill:#6d28d9}</style>
```

so a `color` value like `red}</style><script>fetch('/api/users',...)</script><style>x{` produces a valid SVG that closes the `<style>` element and embeds a `<script>` element. The response Content-Type is `image/svg+xml` (from `pkg/utils/image/image_util.go`), and a grep of the backend confirms no `Content-Security-Policy`, `X-Content-Type-Options`, or framing headers are emitted on any route.

Browsers execute scripts in SVG documents loaded as top-level navigations or via `<iframe src=…>` / `window.open(…)`. The execution context is `origin(arcane-host)`, so the victim's `__Host-token` / `token` HttpOnly JWT cookie (recognized by `extractTokenFromCookieHeaderInternal` at `auth.go:274-286`) is automatically attached to subsequent same-origin `fetch()` calls. From there the attacker can invoke any privileged API the victim possesses — most damagingly `POST /api/users` to create a new admin account, after which the attacker has standalone admin access to manage Docker containers, registries, GitOps secrets, and SSH/registry credentials stored by Arcane.

## Impact

- Same-origin script execution from an unauthenticated, reachable URL — only user interaction (clicking/visiting the crafted link) is required.
- Full session-riding against any authenticated user, including admins. Because Arcane manages Docker daemons, container exec, image registries, and GitOps repositories, an attacker who lands script execution as an admin victim can:
  - Create persistent attacker-controlled admin accounts via `POST /api/users`.
  - Read/modify secrets stored in environments, registries, and Git repositories the admin can access.
  - Start or exec into containers on connected Docker hosts.
- HttpOnly cookies do not mitigate the issue — cookies are auto-attached to same-origin `fetch()`. Absence of CSP and `X-Content-Type-Options: nosniff` removes available defenses-in-depth.

Defense-in-depth — add to all responses (and especially to `/api/app-images/*`):

- `X-Content-Type-Options: nosniff`
- `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:` on the SVG image responses (or the most permissive policy compatible with the frontend on app routes).
- Consider serving these images with `Content-Disposition: inline` and from a separate cookie-less origin to remove the same-origin session-riding primitive entirely.

Also enforce the same allowlist on the settings write path (`SettingsService` → `AccentColor`) so a stored XSS variant cannot be introduced via the settings API.

## References
- https://github.com/getarcaneapp/arcane/security/advisories/GHSA-q2pj-8v84-9mh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45627
- https://github.com/getarcaneapp/arcane
