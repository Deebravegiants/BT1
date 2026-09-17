# [M] SeaweedFS: Improper authorization in the S3Tables / Iceberg REST management API lets a low-privileged S3 user enumerate administrator-owned table buckets

## Summary
Severity: Medium
Advisory: GHSA-hgpf-8634-g44c
CVE: CVE-2026-55873
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-hgpf-8634-g44c
Type: github-advisory

## Affected
- Go: `github.com/seaweedfs/seaweedfs` — affected >=0.0.0-20260128085517-09bb90e8dc16 <0.0.0-20260614205536-b13463880c1f

## Details
### Summary
SeaweedFS routes requests signed with SigV4 service `s3tables` to the S3Tables
management API. Authorization on that path collapsed account-less S3 identities
into the shared `admin` account and failed open, so a user holding only ordinary
S3 `Read` credentials — and no S3Tables-specific permission — could invoke
S3Tables management operations such as `GET /buckets` and enumerate
administrator-owned table bucket inventory (names and ARNs). The same handler
backs the Iceberg REST catalog, which was affected by the same flaw.

### Impact
An authenticated low-privileged S3 user can cross the boundary between ordinary
S3 object access and S3Tables management. Confirmed impact is disclosure of
administrator-owned table bucket inventory (bucket names and ARNs); in shared or
multi-tenant deployments this can reveal tenant naming and operational structure.

### Affected versions
SeaweedFS `>= 4.08, < 4.34` (the S3Tables management API was introduced in 4.08).

### Patched versions
Fixed in **4.34** (#9961). Administrator status is now decided by the
`ACTION_ADMIN` capability rather than by a collapsed `admin` account id, S3Tables
authorization no longer defaults to allow, and the tautological ListTableBuckets
gate was removed. Related hardening of the same root cause landed in #9962,
#9963, and #9971.

### Workaround
No configuration workaround — upgrade to 4.34 or later.

### Credit
Reported by **TA-MU-TA**.

## References
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-hgpf-8634-g44c
- https://nvd.nist.gov/vuln/detail/CVE-2026-55873
- https://github.com/seaweedfs/seaweedfs/pull/9961
- https://github.com/seaweedfs/seaweedfs/commit/b13463880c1fa62e255c058a9228b63cc95b4b36
- https://github.com/seaweedfs/seaweedfs
- https://github.com/seaweedfs/seaweedfs/releases/tag/4.34
