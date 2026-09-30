# [H] Rekor has an OOM Condition due to Unbounded gzip Decompression in Alpine APK Parsing Logic

## Summary
Severity: High
Advisory: GHSA-47q9-m4ww-924m
CVE: CVE-2026-48702
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-47q9-m4ww-924m
Type: github-advisory

## Affected
- Go: `github.com/sigstore/rekor` — affected >=0.3.0 <1.5.2

## Details
## Description

The `Package.Unmarshal()` function in `pkg/types/alpine/apk.go` decompresses the signature and control gzip members of an APK file into in-memory buffers without bounding the total decompressed size. The existing `max_apk_metadata_size` check (default 1MB) is only applied to individual tar entry header sizes after decompression completes, so it does not prevent a decompression bomb from consuming unbounded heap memory.

An attacker can craft a gzip stream that compresses at a ~1000:1 ratio (e.g., 2MB compressed zeros → 2GB decompressed). When submitted as spec.package.content in an Alpine `ProposedEntry`, the server decompresses the full payload into memory during request processing, triggering a fatal Go runtime out-of-memory error or OS OOM-kill that cannot be caught by the server's recover() middleware.

This is reachable via two unauthenticated endpoints:
- POST /api/v1/log/entries (createLogEntry)
- POST /api/v1/log/entries/retrieve (searchLogQuery)

Both invoke `V001Entry.Canonicalize()` → `fetchExternalEntities()` → `apk.Unmarshal(packageData)`, which performs the unbounded decompression.

## Workarounds

There is no effective workaround. Setting `max_request_body_size` reduces but does not eliminate exposure due to the ~1000:1 compression ratio (a 1MB body limit still allows ~1GB heap allocation). Setting `max_apk_metadata_size` has no effect on this vulnerability since the check is applied after decompression.

## References
- https://github.com/sigstore/rekor/security/advisories/GHSA-47q9-m4ww-924m
- https://github.com/sigstore/rekor
