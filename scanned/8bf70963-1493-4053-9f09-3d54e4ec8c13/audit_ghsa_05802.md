# [H] SeaweedFS: Path traversal in the S3 gateway X-Amz-Copy-Source header allows cross-bucket object read

## Summary
Severity: High
Advisory: GHSA-56wq-x3wv-3ff4
CVE: CVE-2026-55874
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-56wq-x3wv-3ff4
Type: github-advisory

## Affected
- Go: `github.com/seaweedfs/seaweedfs` — affected >=0 <0.0.0-20260612000715-b44cf51fe931

## Details
### Summary
The SeaweedFS S3 API gateway did not reject `..` path segments in the `X-Amz-Copy-Source` header used by `CopyObject` and `UploadPartCopy`. The request URL path was hardened against traversal in 4.30 (CVE-2026-54917), but the copy-source header was only checked for emptiness, so a `..` segment in the copy source survived into the server-side filer path and resolved into a different bucket.

### Impact
A confused-deputy authorization bypass that breaks bucket isolation. IAM evaluates the caller's policy against the bucket named in the request URL (the destination the caller owns), while the copy reads its source from the traversed target bucket. An identity scoped to a single bucket (`Read` + `Write` on one bucket it controls) can therefore read any object in any bucket on the instance and land the result in its own bucket.

For example, a caller authorized only for `bucket-a` issues a `CopyObject` into `bucket-a` with copy source `bucket-a/../<victim-bucket>/<key>`; the gateway reads `<victim-bucket>/<key>` and writes it to the attacker-controlled destination, from which the caller reads it normally. `UploadPartCopy` (CopyObjectPartHandler) is affected by the same vector.

### Affected versions
All releases prior to 4.34. The 4.30 fix for CVE-2026-54917 hardened the request URL path but not the `X-Amz-Copy-Source` header.

### Patched version
4.34 and later.

### Remediation
Upgrade to 4.34 or later. The fix validates the copy-source bucket and object key with the same `IsValidBucketName` / `IsValidObjectKey` guards already applied to the request URL, rejecting traversal segments before the handler runs, and applies the same check to `UploadPartCopy`.

### Workaround
No configuration workaround. For deployments that cannot upgrade immediately, front the gateway with a reverse proxy that rejects requests whose `X-Amz-Copy-Source` header contains `..`, `%2e%2e`, or backslash sequences.

### References
- Fix: https://github.com/seaweedfs/seaweedfs/pull/9929 (commit b44cf51fe931bd75aa4d37ae766bea90d7f85ccd)

### Credit
Reported responsibly by [@47Cid](https://github.com/47Cid).

## References
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-56wq-x3wv-3ff4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55874
- https://github.com/seaweedfs/seaweedfs/pull/9929
- https://github.com/seaweedfs/seaweedfs/commit/b44cf51fe931bd75aa4d37ae766bea90d7f85ccd
- https://github.com/seaweedfs/seaweedfs
- https://github.com/seaweedfs/seaweedfs/releases/tag/4.34
