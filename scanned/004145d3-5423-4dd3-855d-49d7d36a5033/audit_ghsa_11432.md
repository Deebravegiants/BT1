# [M] lxd's non-recursive certificate listing bypasses per-object authorization and leaks all fingerprints

## Summary
Severity: Medium
Advisory: GHSA-crmg-9m86-636r
CVE: CVE-2026-3351
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-crmg-9m86-636r
Type: github-advisory

## Affected
- Go: `github.com/canonical/lxd` — affected >=0 <0.0.0-20260224152359-d936c90d47cf

## Details
## Summary
The `GET /1.0/certificates` endpoint (non-recursive mode) returns URLs containing fingerprints for all certificates in the trust store, bypassing the per-object `can_view` authorization check that is correctly applied in the recursive path. Any authenticated identity — including restricted, non-admin users — can enumerate all certificate fingerprints, exposing the full set of trusted identities in the LXD deployment.

## Affected Component
- `lxd/certificates.go` — `certificatesGet` (lines 185–192) — Non-recursive code path returns unfiltered certificate list.

## CWE
- **CWE-862**: Missing Authorization

## Description

### Core vulnerability: missing permission filter in non-recursive listing path

The `certificatesGet` handler obtains a permission checker at line 143 and correctly applies it when building the recursive response (lines 163-176). However, the non-recursive code path at lines 185-192 creates a fresh loop over the unfiltered `baseCerts` slice, completely bypassing the authorization check:

```go
// lxd/certificates.go:139-193
func certificatesGet(d *Daemon, r *http.Request) response.Response {
    recursion := util.IsRecursionRequest(r)
    s := d.State()

    userHasPermission, err := s.Authorizer.GetPermissionChecker(r.Context(), auth.EntitlementCanView, entity.TypeCertificate)
    // ...

    for _, baseCert := range baseCerts {
        if !userHasPermission(entity.CertificateURL(baseCert.Fingerprint)) {
            continue  // Correctly filters unauthorized certs
        }

        if recursion {
            // ... builds filtered certResponses ...
        }
        // NOTE: when !recursion, nothing is recorded — the filter result is discarded
    }

    if !recursion {
        body := []string{}
        for _, baseCert := range baseCerts {  // <-- iterates UNFILTERED baseCerts
            certificateURL := api.NewURL().Path(version.APIVersion, "certificates", baseCert.Fingerprint).String()
            body = append(body, certificateURL)
        }
        return response.SyncResponse(true, body)  // Returns ALL certificate fingerprints
    }

    return response.SyncResponse(true, certResponses)  // Recursive path is correctly filtered
}
```

### Inconsistency with other list endpoints confirms the bug

Five other list endpoints in the same codebase correctly filter results in both recursive and non-recursive paths:

| Endpoint | File | Filters non-recursive? |
|----------|------|----------------------|
| Instances | `lxd/instances_get.go` — `instancesGet` | Yes — filters before either path |
| Images | `lxd/images.go` — `doImagesGet` | Yes — checks `hasPermission` for both paths |
| Networks | `lxd/networks.go` — `networksGet` | Yes — filters outside recursion check |
| Profiles | `lxd/profiles.go` — `profilesGet` | Yes — separate filter in non-recursive path |
| **Certificates** | **`lxd/certificates.go` — `certificatesGet`** | **No — unfiltered** |

The certificates endpoint is the sole outlier, confirming this is an oversight rather than a design choice.

### Access handler provides no defense

The endpoint uses `allowAuthenticated` as its `AccessHandler` (`certificates.go:45`), which only checks `requestor.IsTrusted()`:

```go
// lxd/daemon.go:255-267
// allowAuthenticated is an AccessHandler which allows only authenticated requests.
// This should be used in conjunction with further access control within the handler
// (e.g. to filter resources the user is able to view/edit).
func allowAuthenticated(_ *Daemon, r *http.Request) response.Response {
    requestor, err := request.GetRequestor(r.Context())
    // ...
    if requestor.IsTrusted() {
        return response.EmptySyncResponse
    }
    return response.Forbidden(nil)
}
```

The comment explicitly states that `allowAuthenticated` should be "used in conjunction with further access control within the handler" — which the non-recursive path fails to do.

### Execution chain

1. Restricted authenticated user sends `GET /1.0/certificates` (no `recursion` parameter)
2. `allowAuthenticated` access handler passes because user is trusted (`daemon.go:263`)
3. `certificatesGet` creates permission checker for `EntitlementCanView` on `TypeCertificate` (line 143)
4. Loop at lines 163-176 filters `baseCerts` by permission — but only populates `certResponses` for recursive mode
5. Since `!recursion`, control reaches lines 185-192
6. New loop iterates ALL `baseCerts` (unfiltered) and builds URL list with fingerprints
7. Full list of certificate fingerprints returned to restricted user

## Proof of Concept

```bash
# Preconditions: restricted (non-admin) trusted client certificate
HOST=target.example
PORT=8443

# 1) Non-recursive list: returns ALL certificate fingerprints (UNFILTERED)
curl -sk --cert restricted.crt --key restricted.key \
  "https://${HOST}:${PORT}/1.0/certificates" | jq '.metadata | length'

# 2) Recursive list: returns only authorized certificates (FILTERED)
curl -sk --cert restricted.crt --key restricted.key \
  "https://${HOST}:${PORT}/1.0/certificates?recursion=1" | jq '.metadata | length'

# Expected: (1) returns MORE fingerprints than (2), proving the authorization bypass.
# The difference reveals fingerprints of certificates the restricted user should not see.
```

## Impact

- **Identity enumeration**: A restricted user can discover the fingerprints of all trusted certificates, revealing the complete set of identities in the LXD trust store.
- **Reconnaissance for targeted attacks**: Fingerprints identify specific certificates used for inter-cluster communication, admin access, and other privileged operations.
- **RBAC bypass**: In deployments using fine-grained RBAC (OpenFGA or built-in TLS authorization), the non-recursive path completely bypasses the intended per-object visibility controls.
- **Information asymmetry**: Restricted users gain knowledge of the full trust topology, which the administrator explicitly intended to hide via per-certificate `can_view` entitlements.

## Recommended Remediation

### Option 1: Apply the permission filter to the non-recursive path (preferred)

Replace the unfiltered loop with one that checks `userHasPermission`, matching the pattern used in the recursive path and in all other list endpoints:

```go
// lxd/certificates.go — replace lines 185-192
if !recursion {
    body := []string{}
    for _, baseCert := range baseCerts {
        if !userHasPermission(entity.CertificateURL(baseCert.Fingerprint)) {
            continue
        }
        certificateURL := api.NewURL().Path(version.APIVersion, "certificates", baseCert.Fingerprint).String()
        body = append(body, certificateURL)
    }
    return response.SyncResponse(true, body)
}
```

### Option 2: Build both response types in a single filtered loop

Restructure the function to build both the URL list and the recursive response in the same permission-checked loop, eliminating the possibility of divergent filtering:

```go
err = d.State().DB.Cluster.Transaction(r.Context(), func(ctx context.Context, tx *db.ClusterTx) error {
    baseCerts, err = dbCluster.GetCertificates(ctx, tx.Tx())
    if err != nil {
        return err
    }

    certResponses = make([]*api.Certificate, 0, len(baseCerts))
    certURLs = make([]string, 0, len(baseCerts))
    for _, baseCert := range baseCerts {
        if !userHasPermission(entity.CertificateURL(baseCert.Fingerprint)) {
            continue
        }

        certURLs = append(certURLs, api.NewURL().Path(version.APIVersion, "certificates", baseCert.Fingerprint).String())

        if recursion {
            apiCert, err := baseCert.ToAPI(ctx, tx.Tx())
            if err != nil {
                return err
            }
            certResponses = append(certResponses, apiCert)
            urlToCertificate[entity.CertificateURL(apiCert.Fingerprint)] = apiCert
        }
    }
    return nil
})
```

Option 2 is structurally safer as it prevents the two paths from diverging in the future.

## Credit
This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/canonical/lxd/security/advisories/GHSA-crmg-9m86-636r
- https://nvd.nist.gov/vuln/detail/CVE-2026-3351
- https://github.com/canonical/lxd/pull/17738
- https://github.com/canonical/lxd/commit/d936c90d47cf0be1e9757df897f769e9887ebde1
- https://github.com/canonical/lxd
