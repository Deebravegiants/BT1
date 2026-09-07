# [M] Canonical LXD Project Existence Determination Through Error Handling in Image Export Function

## Summary
Severity: Medium
Advisory: GHSA-p3x5-mvmp-5f35
CVE: CVE-2025-54290
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-02
Source: https://github.com/advisories/GHSA-p3x5-mvmp-5f35
Type: github-advisory

## Affected
- Go: `github.com/canonical/lxd` — affected >=4.0 <5.21.4
- Go: `github.com/canonical/lxd` — affected >=6.0 <6.5
- Go: `github.com/canonical/lxd` — affected >=0.0.0-20200331193331-03aab09f5b5c <0.0.0-20250827065555-0494f5d47e41

## Details
### Impact
In LXD's images export API (`/1.0/images/{fingerprint}/export`), implementation differences in error handling allow determining project existence without authentication.

Specifically, in the following code, errors when multiple images match are directly returned to users as API responses:

https://github.com/canonical/lxd/blob/43d5189564d27f6161b430ed258c8b56603c2759/lxd/db/images.go#L239-L246

While fingerprints generally don't duplicate, this functionality uses fingerprints with LIKE clauses, allowing prefix specification. Therefore, using LIKE wildcards such as % will match multiple images if multiple images exist in the project.

https://github.com/canonical/lxd/blob/43d5189564d27f6161b430ed258c8b56603c2759/lxd/db/images.go#L277-L286

In the above implementation, multiple matches result in a 500 error, but if the project itself doesn't exist, there are 0 matches and a 404 is returned.

1. When project exists and multiple images match: HTTP 500 error "More than one image matches"
2. When project doesn't exist: HTTP 404 error "not found" 
 
This behavioural difference allows attackers to confirm project existence without authentication.

### Reproduction Steps
1. Send a request with a pattern matching multiple entries to an existing project (default):

```
curl -k 'https://lxd-host:8443/1.0/images/%25/export?project=default&secret=x'
```

Response:

```json
{"type":"error","status":"","status_code":0,"operation":"","error_code":500,"error":"More than one image matches","metadata":null}
```

2. Send a same request to a non-existent project (not-exist):

```
curl -k 'https://lxd-host:8443/1.0/images/%25/export?project=not-exist&secret=x'
```

Response:

```json
{"type":"error","status":"","status_code":0,"operation":"","error_code":404,"error":"not found","metadata":null}
```

This difference allows enumerating existing projects in the system by brute-forcing(dictionary attack) project names.

Note that `%25` is the URL encoding of `%`, which works as a wildcard matching all characters in SQL LIKE clauses. 
This is used to intentionally create requests matching multiple images to trigger a 500 error.

Additionally, the secret parameter is added to include non-public images in the search, increasing the possibility of multiple matches.

https://github.com/canonical/lxd/blob/43d5189564d27f6161b430ed258c8b56603c2759/lxd/images.go#L4211-L4230

### Risk
The attack requires only network access to the LXD API endpoint, with no authentication needed.

The attack allows confirming the existence of projects within the LXD system by exploiting differences in HTTP status codes. This could potentially increase the exploitability of other vulnerabilities. Additionally, since project IDs often use meaningful names set by users, this could lead to leakage of unpublished product information. 

However, resource information within projects cannot be obtained, limiting the impact to existence confirmation only.

### Countermeasures
It is recommended to modify error handling in the images export API (`/1.0/images/{fingerprint}/export`) to return consistent responses regardless of project existence. 

Specifically, return 404 even when errors occur during project existence verification.
This ensures the same error response is returned for both existing and non-existing projects, preventing determination of project existence.

Additionally, if there are no specification(compatibility) issues, allowing only exact fingerprint matches in unauthenticated states and disabling prefix matching can prevent unexpected errors from occurring.

### Patches

| LXD Series  | Status |
| ------------- | ------------- |
| 6 | Fixed in LXD 6.5  |
| 5.21 | Fixed in LXD 5.21.4  |
| 5.0 | Ignored - Not critical |
| 4.0  | Ignored - EOL and not critical |

### References
Reported by GMO Flatt Security Inc.

## References
- https://github.com/canonical/lxd/security/advisories/GHSA-p3x5-mvmp-5f35
- https://nvd.nist.gov/vuln/detail/CVE-2025-54290
- https://github.com/canonical/lxd
- https://pkg.go.dev/vuln/GO-2025-4002
