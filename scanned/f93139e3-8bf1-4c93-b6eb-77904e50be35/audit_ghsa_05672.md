# [M] sigstore legacy TUF client allows for arbitrary file writes with target cache path traversal

## Summary
Severity: Medium
Advisory: GHSA-fcv2-xgw5-pqxf
CVE: CVE-2026-24137
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-fcv2-xgw5-pqxf
Type: github-advisory

## Affected
- Go: `github.com/sigstore/sigstore` — affected >=0 <1.10.4

## Details
## Summary

The legacy TUF client `pkg/tuf/client.go`, which supports caching target files to disk, constructs a filesystem path by joining a cache base directory with a target name sourced from signed target metadata, but it does not validate that the resulting path stays within the cache base directory.

Note that this should only affect clients that are directly using the TUF client in sigstore/sigstore or are using an older version of Cosign. As this TUF client implementation is deprecated, users should migrate to https://github.com/sigstore/sigstore-go/tree/main/pkg/tuf as soon as possible.

Note that this does not affect users of the public Sigstore deployment, where TUF metadata is validated by a quorum of trusted collaborators. 

## Impact

A malicious TUF repository can trigger arbitrary file overwriting, limited to the permissions that the calling process has.

## Workarounds

Users can disable disk caching for the legacy client by setting `SIGSTORE_NO_CACHE=true` in the environment, migrate to https://github.com/sigstore/sigstore-go/tree/main/pkg/tuf, or upgrade to the latest sigstore/sigstore release.

## References
- https://github.com/sigstore/sigstore/security/advisories/GHSA-fcv2-xgw5-pqxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-24137
- https://github.com/sigstore/sigstore/commit/8ec410a2993ea78083aecf0e473a85453039496e
- https://github.com/sigstore/sigstore
- https://github.com/sigstore/sigstore/releases/tag/v1.10.4
- https://pkg.go.dev/vuln/GO-2026-4358
