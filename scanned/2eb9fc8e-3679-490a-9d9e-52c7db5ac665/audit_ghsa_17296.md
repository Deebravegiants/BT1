# [M] Traefik Inverted TLS Verification Logic in ingress-nginx Provider

## Summary
Severity: Medium
Advisory: GHSA-7vww-mvcr-x6vj
CVE: CVE-2025-66491
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-7vww-mvcr-x6vj
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.5.0 <3.6.3

## Details
## Impact

There is a potential vulnerability in Traefik NGINX provider managing the `nginx.ingress.kubernetes.io/proxy-ssl-verify` annotation.

The provider inverts the semantics of the `nginx.ingress.kubernetes.io/proxy-ssl-verify` annotation. Setting the annotation to `"on"` (intending to enable backend TLS certificate verification) actually disables verification, allowing man-in-the-middle attacks against HTTPS backends when operators believe they are protected.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.6.3

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary

A logic error in Traefik's experimental ingress-nginx provider inverts the semantics of the `nginx.ingress.kubernetes.io/proxy-ssl-verify` annotation. Setting the annotation to `"on"` (intending to enable backend TLS certificate verification) actually disables verification, allowing man-in-the-middle attacks against HTTPS backends when operators believe they are protected.

### Details

In `pkg/provider/kubernetes/ingress-nginx/kubernetes.go` at line 512, the `InsecureSkipVerify` field is set using inverted logic:

```go
nst := &namedServersTransport{
    Name: provider.Normalize(namespace + "-" + name),
    ServersTransport: &dynamic.ServersTransport{
        ServerName:         ptr.Deref(cfg.ProxySSLName, ptr.Deref(cfg.ProxySSLServerName, "")),
        InsecureSkipVerify: strings.ToLower(ptr.Deref(cfg.ProxySSLVerify, "off")) == "on",
    },
}
```

The expression `== "on"` evaluates to `true` when the annotation is `"on"`, setting `InsecureSkipVerify: true`. In Go's `crypto/tls`, `InsecureSkipVerify: true` means "do not verify the server's certificate" — the opposite of what `proxy-ssl-verify: "on"` should do according to NGINX semantics.

**Current behavior:**
| Annotation Value | InsecureSkipVerify | Actual Result |
|------------------|-------------------|---------------|
| `"on"` | `true` | Verification **disabled** ❌ |
| `"off"` (default) | `false` | Verification **enabled** |

**Expected behavior (per NGINX semantics):**
| Annotation Value | InsecureSkipVerify | Expected Result |
|------------------|-------------------|-----------------|
| `"on"` | `false` | Verification **enabled** |
| `"off"` (default) | `true` | Verification **disabled** |

The test in `pkg/provider/kubernetes/ingress-nginx/kubernetes_test.go` lines 397-403 confirms this inverted behavior is codified as "expected":

```go
ServersTransports: map[string]*dynamic.ServersTransport{
    "default-ingress-with-proxy-ssl": {
        ServerName:         "whoami.localhost",
        InsecureSkipVerify: true,  // Wrong: should be false when annotation is "on"
        RootCAs:            []types.FileOrContent{"-----BEGIN CERTIFICATE-----"},
    },
},
```

**Affected versions:** v3.5.0 through current master (introduced in commit `9bd5c617820f2a8d23b50b68d114bb7bc464eccd`)

Pavel Kohout
Aisle Research
</details>

-

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-7vww-mvcr-x6vj
- https://nvd.nist.gov/vuln/detail/CVE-2025-66491
- https://github.com/traefik/traefik/commit/14a1aedf5704673d875d210d7bacf103a43c77e4
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v3.6.3
