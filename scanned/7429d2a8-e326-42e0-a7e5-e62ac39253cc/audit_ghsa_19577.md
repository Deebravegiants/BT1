# [H] MinIO performs incomplete signature validation for unsigned-trailer uploads

## Summary
Severity: High
Advisory: GHSA-wg47-6jq2-q2hh
CVE: CVE-2025-31489
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-wg47-6jq2-q2hh
Type: github-advisory

## Affected
- Go: `github.com/minio/minio` — affected >=0 <0.0.0-20250403145552-8c70975283f9

## Details
### Impact
This is a high priority vulnerability and users must upgrade ASAP.

The signature component of the authorization may be invalid, which would mean that as a client you can use any arbitrary secret to upload objects given the user already has prior WRITE permissions on the bucket,

Prior knowledge of access-key, and bucket name this user might have access to - and an access-key with a WRITE permissions is necessary.

However with relevant information in place, uploading random objects to buckets is trivial and easy via `curl`

### Patches
Yes https://github.com/minio/minio/pull/21103

### Workarounds
Reject requests with `x-amz-content-sha256: STREAMING-UNSIGNED-PAYLOAD-TRAILER` for now at LB layer, ask application users to use `STREAMING-AWS4-HMAC-SHA256-PAYLOAD-TRAILER`

## References
- https://github.com/minio/minio/security/advisories/GHSA-wg47-6jq2-q2hh
- https://nvd.nist.gov/vuln/detail/CVE-2025-31489
- https://github.com/minio/minio/pull/21103
- https://github.com/minio/minio/commit/8c70975283f9f4ce80f331a25c7475a36279e519
- https://github.com/minio/minio
