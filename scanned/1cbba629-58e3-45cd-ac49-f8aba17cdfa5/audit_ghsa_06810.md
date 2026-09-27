# [M] Kite Kubernetes proxy path traversal allows authenticated users to bypass RBAC and read cluster-wide resources

## Summary
Severity: Medium
Advisory: GHSA-c534-2w9c-x7fm
CWE: CWE-647
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-c534-2w9c-x7fm
Type: github-advisory

## Affected
- Go: `github.com/zxh326/kite` — affected >=0.6.9 <0.14.1

## Details
## Summary

Kite versions 0.6.9 through 0.14.0 authorize Kubernetes proxy requests against the pod or service identified by the original route parameters. Encoded path traversal segments can cause the upstream URL to resolve to a different Kubernetes API endpoint after authorization.

## Impact

An authenticated user with `get` permission on pods or services in one namespace can cause Kite to issue GET requests to Kubernetes API endpoints outside that namespace using Kite's service account.

With Kite's default Helm RBAC configuration, this allows cluster-wide resource disclosure, including Secrets. The validated impact is confidentiality only; resource modification and denial of service were not demonstrated.

Deployments using a restricted Kite service account are affected only up to the permissions granted to that service account.

## Technical details

The authorization check is performed against the original namespace and kind route parameters. The proxy path is subsequently decoded and passed to `url.JoinPath`, which resolves `..` segments and can produce an upstream URL outside the authorized pod or service proxy prefix.

Two input locations were affected:

1. Encoded traversal segments in the proxy catch-all path.
2. Encoded traversal and slash characters in the resource name.

## Reproduction


1. Create a user with a role granting only `pods:get` in namespace `default`.
2. Create any pod in `default` (e.g. `nginx`).
3. Send the following request (auth cookie required):

```bash
curl --path-as-is --cookie "auth_token=<JWT>" \
  'http://<kite-host>/api/v1/_clusters/<cluster>/namespaces/default/pods/nginx/proxy/%2e%2e/%2e%2e/%2e%2e/%2e%2e/kube-system/secrets'
```

## Patches

Fixed in Kite 0.14.1.

- https://github.com/kite-org/kite/releases/tag/v0.14.1

## Workarounds

Upgrade to 0.14.1 or later.

If upgrading is temporarily impossible, reject encoded dot segments and encoded slashes at the reverse proxy and restrict Kite's Kubernetes service account permissions. Reverse-proxy normalization should not be treated as a permanent fix.

## References
- https://github.com/kite-org/kite/security/advisories/GHSA-c534-2w9c-x7fm
- https://github.com/kite-org/kite/pull/638
- https://github.com/kite-org/kite/commit/08116eed557f8d6982cc83af0b02991e0f3577d5
- https://github.com/kite-org/kite/commit/69ad938937af8f375a2e183d1a331926ab851d98
- https://github.com/kite-org/kite
- https://github.com/kite-org/kite/releases/tag/v0.14.1
