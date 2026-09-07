# [M] Traefik Kubernetes Ingress NGINX provider fails open when auth-secret resolution fails

## Summary
Severity: Medium
Advisory: GHSA-4mr2-fg2p-w63c
CVE: CVE-2026-54762
CWE: CWE-636, CWE-693
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-4mr2-fg2p-w63c
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.5

## Details
## Summary

There is a medium severity vulnerability in Traefik's Kubernetes Ingress NGINX provider that causes affected routes to fail open. When an Ingress explicitly enables BasicAuth or DigestAuth through the supported `nginx.ingress.kubernetes.io/auth-type` and `auth-secret` annotations, but the referenced auth Secret cannot be resolved or parsed, Traefik logs the resolution error, skips installing the authentication middleware, and still emits a router to the backend service. A route that operators intended to protect is therefore published to the data plane without its authentication control, allowing unauthenticated access to the backend. The trigger is an invalid or unresolved auth dependency — a missing, malformed, unreadable, or policy-denied Secret — rather than an intentionally unprotected route.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.7.5

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary

Traefik's Kubernetes Ingress NGINX provider can fail open for routes that explicitly configure BasicAuth or DigestAuth through supported ingress-nginx annotations.

When an Ingress contains `nginx.ingress.kubernetes.io/auth-type: basic` or `digest`, but the referenced `nginx.ingress.kubernetes.io/auth-secret` cannot be resolved or parsed, Traefik logs the auth resolution error, skips installing the BasicAuth/DigestAuth middleware, and still emits a router to the backend service.

This can expose a route that operators intended to protect. The issue is not that an invalid Secret exists; the issue is that an explicitly auth-protected Ingress location is translated into a live backend route where the authentication control is removed from the generated data-plane configuration, with only a controller log entry, instead of failing closed.

Tested affected versions:

- Current `master`: `29406d42898547f1ffabd904f66af06c212740cf`
- Latest tag tested by me: `v3.7.1` / `fa49e2bcad7ffd8a80accdf1fae1ae480913d93d`

The KubernetesIngressNGINX provider is documented as no longer experimental as of v3.6.2, and the `auth-type`, `auth-secret`, `auth-secret-type`, and `auth-realm` annotations are documented supported annotations.

### Details

The root cause is in `pkg/provider/kubernetes/ingress-nginx/build.go`. During provider translation, auth is pre-resolved for each location:

```go
if ing.config.AuthType != nil {
    basic, digest, err := p.resolveBasicAuth(ing.Namespace, ing.config)
    if err != nil {
        logger.Error().
            Err(err).
            Str("ingress", fmt.Sprintf("%s/%s rule-%d path-%d", ing.Namespace, ing.Name, ri, pi)).
            Msg("Cannot resolve auth secret, skipping auth middleware")
    } else {
        loc.BasicAuth = basic
        loc.DigestAuth = digest
    }
}
```

The error is logged, but `loc.Error` is not set. Later, `pkg/provider/kubernetes/ingress-nginx/translator.go` only routes to `unavailable-service` when `loc.Error` is true. Since this auth error leaves `loc.Error` false, the generated router continues to use the real backend service, and `applyMiddlewares` has no BasicAuth/DigestAuth middleware to attach.

This differs from nearby fail-closed behavior for comparable provider translation failures:

- `auth-tls-secret` resolution failure skips the affected ingress.
- `custom-headers` ConfigMap resolution failure sets `loc.Error = true`, causing the translator to avoid normal backend exposure.

Security invariant:

> If an Ingress location explicitly configures BasicAuth/DigestAuth, Traefik should not forward that location to the backend unless the corresponding auth middleware is installed.

Reasonable fail-closed behaviors would include omitting the router, routing it to `unavailable-service`, returning 503, or attaching a deny-all middleware until the auth dependency is valid.

### Expected behavior

An Ingress location with explicit `auth-type: basic` or `auth-type: digest` must not forward requests to the backend unless the generated Traefik router has the corresponding BasicAuth/DigestAuth middleware attached.

If the referenced auth Secret is missing, malformed, unreadable, denied by namespace policy, or otherwise unusable, Traefik should fail closed for that location.

### Actual behavior

When `auth-secret` resolution fails, Traefik still creates a router to the backend service and only omits the BasicAuth/DigestAuth middleware. The only indication is a controller log entry:

```text
Cannot resolve auth secret, skipping auth middleware
```

### PoC

I reproduced this with a clean fake Kubernetes provider state. The reproduction does not use Docker provider labels, dashboard/API routing, lab backends, or public network targets.

Minimal Kubernetes objects:

- `IngressClass` named `nginx` with controller `k8s.io/ingress-nginx`
- `Service` named `whoami` in namespace `default`
- `EndpointSlice` for the `whoami` service
- `Ingress` with `ingressClassName: nginx`, a backend pointing to `whoami`, and these annotations:

```yaml
nginx.ingress.kubernetes.io/auth-type: "basic"
nginx.ingress.kubernetes.io/auth-secret-type: "auth-file"
nginx.ingress.kubernetes.io/auth-secret: "default/missing-basic-auth"
```

The referenced Secret intentionally does not exist. The expected secure behavior is fail-closed for this auth-configured route. The observed behavior is a normal router to the backend without BasicAuth/DigestAuth.

Key failing assertion from the regression harness:

```text
router forwards to backend service without BasicAuth/DigestAuth when auth-secret is missing; middlewares=[default-auth-missing-secret-rule-0-path-0-retry] service="default-auth-missing-secret-whoami-80"
```

The same behavior reproduces on both current `master` and `v3.7.1`.

I also tested a matrix of auth-secret resolution failures. In each error case, Traefik still emitted the backend router without BasicAuth/DigestAuth:

- missing `auth-secret`
- omitted/empty `auth-secret`
- invalid `auth-secret-type`
- `auth-file` Secret missing the required `auth` key
- empty `auth-map` Secret
- missing DigestAuth Secret
- cross-namespace `auth-secret` denied by default policy

The same matrix includes a positive control where a valid `auth-file` Secret correctly attaches BasicAuth, confirming that the harness is exercising the intended provider path.

I also performed a clean-room revalidation from fresh `git archive` source trees for both source/master and v3.7.1. Only the two minimal test harnesses were copied into each archived source tree. This avoided contamination from lab compose files, Docker provider state, dashboard/API routes, prior source-tree test files, or running lab backends.

### Threat model

This does not require an attacker to modify Traefik static configuration or Traefik process state. The relevant security boundary is the Kubernetes-declared route policy: an Ingress explicitly declares BasicAuth/DigestAuth, but Traefik publishes the data-plane route without that control when the auth dependency is invalid.

In multi-tenant or GitOps-managed clusters, the actor or automation that can affect Secret existence, Secret contents, namespace policy, or deployment ordering is not necessarily the same actor that owns the protected backend or Traefik deployment. As a result, a mistake, rollback, pruning job, policy change, or compromise limited to Kubernetes application resources can remove the effective auth boundary while the Ingress continues to declare that auth is required.

### Impact

This is a fail-open authentication control issue leading to unintended unauthenticated route exposure.

The trigger is an invalid or unresolved auth dependency, but the security consequence is a data-plane route that violates explicit auth intent. This is materially different from intentionally deploying an unprotected route: the Ingress declares `auth-type: basic` or `digest`, yet Traefik publishes the backend without the corresponding auth middleware.

Realistic scenarios include:

- GitOps, Helm, or CI/CD deploys Ingress and Secret resources separately. Ordering issues, rollbacks, pruning, or typos can leave the Ingress active while the auth Secret is absent or unreadable.
- Kubernetes RBAC commonly separates ownership of Ingress objects, Secrets, and namespace policies. A lower-privileged namespace actor or deployment automation may be able to affect the referenced Secret or cross-namespace reference outcome without having direct access to Traefik static configuration.
- During ingress-nginx migration, operators reasonably expect supported `nginx.ingress.kubernetes.io/auth-*` annotations to preserve the authentication boundary. Publishing the backend without auth is a worse failure mode than rejecting the invalid location.
- A transient Secret deletion, malformed Secret update, or policy change can turn an already protected route into an unprotected route without changing the Ingress rule itself.

Controller logs are not a sufficient mitigation. Logs do not prevent exposure, may not page the service owner, and the first externally visible symptom can be unauthenticated access to the protected backend.

### Suggested remediation

Fail closed on any `resolveBasicAuth` error. A minimal tested change is to mark the location as errored:

```diff
 if err != nil {
     logger.Error().
         Err(err).
         Str("ingress", fmt.Sprintf("%s/%s rule-%d path-%d", ing.Namespace, ing.Name, ri, pi)).
         Msg("Cannot resolve auth secret, skipping auth middleware")
+    loc.Error = true
 } else {
```

This reuses the existing `loc.Error` / `unavailable-service` path. In my local validation, this change made the no-backend-without-auth regression pass while preserving the valid-secret positive control.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-4mr2-fg2p-w63c
- https://nvd.nist.gov/vuln/detail/CVE-2026-54762
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.7.5
