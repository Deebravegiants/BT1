# [M] goshs has ACL Bypass & Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-964w-f6gj-5236
CVE: CVE-2026-66064
CWE: CWE-22, CWE-41, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-964w-f6gj-5236
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs/v2` — affected >=0 <2.1.5-0.20260727065949-f3ef599e4091
- Go: `goshs.de/goshs/v2` — affected >=0 <2.1.5-0.20260727065949-f3ef599e4091
- Go: `github.com/patrickhener/goshs` — affected >=0
- Go: `goshs.de/goshs` — affected >=0

## Details
## Summary

`sendFile` derives the served filename from the raw request path while opening the file from the cleaned path, so appending a trailing slash empties the derived name and defeats both the never-serve rule for the ACL file and the block list. 

## Finding (Medium): trailing-slash ACL and hidden-file bypass

httpserver/handler.go, sendFile (lines 789-801) takes the filename from the RAW req.URL.Path while the file itself is opened from the filepath.Clean-ed path. The two disagree, and a trailing slash makes the derived name the empty string. Both protections key on that derived name, so both are defeated: the rule that never serves the .goshs ACL file, and the acl.Block list.

Measured, with negative controls:

```
GET /blocked/secret.txt    -> 404          (control, correctly blocked)
GET /blocked/secret.txt/   -> 200 + contents
GET /blocked/.goshs/       -> 200, returns the ACL file itself,
                              including the admin:$2a$... bcrypt hash
```

Unauthenticated when the ACL is configured block-only (common usage). Stated precisely: AUTHENTICATION IS NOT BYPASSED. An unauthenticated request against a directory protected by authentication still returns 401 under the same trick; I tested that. The claim is specifically that the block list and the ACL-file protection are bypassed. In-tree evidence that sendFile is the defect: the sibling handlers doDir and bulkDownload both derive the name correctly; sendFile is the lone outlier.

## Suggested fixes

1. Derive the served filename from the same cleaned path used to open the file, so the authorization decision and the file access cannot disagree.

## Tooling

AI assistance was used while investigating. The finding was reproduced against a running server on loopback with negative controls, including the 404-versus-200 pair and the authenticated-directory control that shows authentication is not affected.

## References
- https://github.com/goshs-labs/goshs/security/advisories/GHSA-964w-f6gj-5236
- https://github.com/goshs-labs/goshs/pull/222
- https://github.com/goshs-labs/goshs/commit/f3ef599e409151d1380866e47de8b1afb0bb54fa
- https://github.com/goshs-labs/goshs
