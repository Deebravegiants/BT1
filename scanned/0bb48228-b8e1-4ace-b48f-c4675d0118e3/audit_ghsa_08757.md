# [M] Incus has Nil-Pointer Dereference via S3 Bucket Import

## Summary
Severity: Medium
Advisory: GHSA-fwj8-62r8-8p8m
CVE: CVE-2026-41647
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-fwj8-62r8-8p8m
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6/cmd/incusd` — affected >=0

## Details
### Summary
Missing error handling could lead an authenticated Incus user to cause a daemon crash through the import of a truncated storage bucket backup file.

### Details
It was found that TransferManager.UploadAllFiles iterates over tar entries but only checks for io.EOF from tr.Next(). When tr.Next() returns a non-EOF error, such as unexpected EOF from a truncated archive, the header hdr is nil and the code continues to access hdr.Name, causing a nil-pointer dereference that panics the daemon.

This may allow the Incus daemon to be crashed during S3 bucket restore if a truncated or corrupted backup archive is provided. A panic can occur when a malformed archive produces a non-EOF tar read error after the first entry. Any caller of UploadAllFiles that processes attacker-controlled archive content may be affected.

Affected File:
[https://github.com/lxc/incus/blob/v6.22.0/…server/storage/s3/transfer_manager.go#L127](https://github.com/lxc/incus/blob/v6.22.0/internal/server/storage/s3/transfer_manager.go#L127) 

The tar-iteration loop only checks for EOF:

Affected Code:
```
for {
    hdr, err := tr.Next()
    if err == io.EOF {
        break // End of archive.
    }

    // Skip index.yaml file
    if hdr.Name == "backup/index.yaml" {
```

When tr.Next() returns a non-EOF error, hdr is nil. The code does not check for this case and immediately dereferences hdr.Name.

This was confirmed as follows:

Command:
```
go test ./test/fuzz -run='FuzzS3BucketUploadTarParsing/s3_nil_deref_truncated_tar' -count=1 -v
```

Output:
```
=== RUN   FuzzS3BucketUploadTarParsing
=== RUN   FuzzS3BucketUploadTarParsing/s3_nil_deref_truncated_tar
   s3_bucket_upload_fuzz_test.go:82: UploadAllFiles panicked: runtime error: invalid memory address
       or nil pointer dereference
--- FAIL: FuzzS3BucketUploadTarParsing/s3_nil_deref_truncated_tar (0.00s)
FAIL
```

It is recommended to add a non-EOF error check after tr.Next().

Proposed Fix:
```
hdr, err := tr.Next()
if err == io.EOF {
    break
}

if err != nil {
    return fmt.Errorf("Error reading backup archive: %w", err)
}
```

A patch is available at https://github.com/lxc/incus/releases/tag/v7.0.0.

### Credits
This issue was discovered and reported by the team at 7asecurity (https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-fwj8-62r8-8p8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-41647
- https://github.com/lxc/incus
- https://github.com/lxc/incus/releases/tag/v7.0.0
