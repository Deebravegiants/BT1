# [M] Cosign malicious attachments can cause system-wide denial of service

## Summary
Severity: Medium
Advisory: GHSA-88jx-383q-w4qc
CVE: CVE-2024-29902
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-11
Source: https://github.com/advisories/GHSA-88jx-383q-w4qc
Type: github-advisory

## Affected
- Go: `github.com/sigstore/cosign` — affected >=0
- Go: `github.com/sigstore/cosign/v2` — affected >=0 <2.2.4

## Details
### Summary
A remote image with a malicious attachment can cause denial of service of the host machine running Cosign. This can impact other services on the machine that rely on having memory available such as a Redis database which can result in data loss. It can also impact the availability of other services on the machine that will not be available for the duration of the machine denial.

### Details
The root cause of this issue is that Cosign reads the attachment from a remote image entirely into memory without checking the size of the attachment first. As such, a large attachment can make Cosign read a large attachment into memory; If the attachments size is larger than the machine has memory available, the machine will be denied of service. The Go runtime will make a `SIGKILL` after a few seconds of system-wide denial.

The root cause is that Cosign reads the contents of the attachments entirely into memory on line 238 below:

https://github.com/sigstore/cosign/blob/9bc3ee309bf35d2f6e17f5d23f231a3d8bf580bc/pkg/oci/remote/remote.go#L228-L239

...and prior to that, neither Cosign nor go-containerregistry checks the size of the attachment and enforces a max cap. In the case of a remote layer of `f *attached`, go-containerregistry will invoke this API:

https://github.com/google/go-containerregistry/blob/a0658aa1d0cc7a7f1bcc4a3af9155335b6943f40/pkg/v1/remote/layer.go#L36-L40
```golang
func (rl *remoteLayer) Compressed() (io.ReadCloser, error) {
	// We don't want to log binary layers -- this can break terminals.
	ctx := redact.NewContext(rl.ctx, "omitting binary blobs from logs")
	return rl.fetcher.fetchBlob(ctx, verify.SizeUnknown, rl.digest)
}
```

Notice that the second argument to `rl.fetcher.fetchBlob` is `verify.SizeUnknown` which results in not using the `io.LimitReader` in `verify.ReadCloser`:
https://github.com/google/go-containerregistry/blob/a0658aa1d0cc7a7f1bcc4a3af9155335b6943f40/internal/verify/verify.go#L82-L100
```golang
func ReadCloser(r io.ReadCloser, size int64, h v1.Hash) (io.ReadCloser, error) {
	w, err := v1.Hasher(h.Algorithm)
	if err != nil {
		return nil, err
	}
	r2 := io.TeeReader(r, w) // pass all writes to the hasher.
	if size != SizeUnknown {
		r2 = io.LimitReader(r2, size) // if we know the size, limit to that size.
	}
	return &and.ReadCloser{
		Reader: &verifyReader{
			inner:    r2,
			hasher:   w,
			expected: h,
			wantSize: size,
		},
		CloseFunc: r.Close,
	}, nil
}
```

### Impact
This issue can allow a supply-chain escalation from a compromised registry to the Cosign user: If an attacher has compromised a registry or the account of an image vendor, they can include a malicious attachment and hurt the image consumer. 

### Remediation
Update to the latest version of Cosign, which limits the number of attachments. An environment variable can override this value.

## References
- https://github.com/sigstore/cosign/security/advisories/GHSA-88jx-383q-w4qc
- https://nvd.nist.gov/vuln/detail/CVE-2024-29902
- https://github.com/sigstore/cosign/commit/629f5f8fa672973503edde75f84dcd984637629e
- https://github.com/google/go-containerregistry/blob/a0658aa1d0cc7a7f1bcc4a3af9155335b6943f40/pkg/v1/remote/layer.go#L36-L40
- https://github.com/sigstore/cosign
- https://github.com/sigstore/cosign/blob/9bc3ee309bf35d2f6e17f5d23f231a3d8bf580bc/pkg/oci/remote/remote.go#L228-L239
- https://github.com/sigstore/cosign/releases/tag/v2.2.4
