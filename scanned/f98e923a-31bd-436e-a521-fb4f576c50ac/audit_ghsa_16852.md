# [M] Cosign malicious artifacts can cause machine-wide DoS

## Summary
Severity: Medium
Advisory: GHSA-95pr-fxf5-86gv
CVE: CVE-2024-29903
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-11
Source: https://github.com/advisories/GHSA-95pr-fxf5-86gv
Type: github-advisory

## Affected
- Go: `github.com/sigstore/cosign` — affected >=0
- Go: `github.com/sigstore/cosign/v2` — affected >=0 <2.2.4

## Details
Maliciously-crafted software artifacts can cause denial of service of the machine running Cosign, thereby impacting all services on the machine. The root cause is that Cosign creates slices based on the number of signatures, manifests or attestations in untrusted artifacts. As such, the untrusted artifact can control the amount of memory that Cosign allocates.  

As an example, these lines demonstrate the problem:

https://github.com/sigstore/cosign/blob/286a98a4a99c1b2f32f84b0d560e324100312280/pkg/oci/remote/signatures.go#L56-L70 

This `Get()` method gets the manifest of the image, allocates a slice equal to the length of the layers in the manifest, loops through the layers and adds a new signature to the slice.

The exact issue is Cosign allocates excessive memory on the lines that creates a slice of the same length as the manifests. 

## Remediation

Update to the latest version of Cosign, where the number of attestations, signatures and manifests has been limited to a reasonable value.

## Cosign PoC

In the case of this API (also referenced above):

https://github.com/sigstore/cosign/blob/286a98a4a99c1b2f32f84b0d560e324100312280/pkg/oci/remote/signatures.go#L56-L70

… The first line can contain a length that is safe for the system and will not throw a runtime panic or be blocked by other safety mechanisms. For the sake of argument, let’s say that the length of `m, err := s.Manifest()` is the max allowed (by the machine without throwing OOM panics) manifests minus 1. When Cosign then allocates a new slice on this line: `signatures := make([]oci.Signature, 0, len(m.Layers))`, Cosign will allocate more memory than is available and the machine will be denied of service, causing Cosign and all other services on the machine to be unavailable.

To illustrate the issue here, we run a modified version of `TestSignedImageIndex()` in `pkg/oci/remote`:

https://github.com/sigstore/cosign/blob/14795db16417579fac0c00c11e166868d7976b61/pkg/oci/remote/index_test.go#L31-L57

Here, `wantLayers` is the number of manifests from these lines:

https://github.com/sigstore/cosign/blob/286a98a4a99c1b2f32f84b0d560e324100312280/pkg/oci/remote/signatures.go#L56-L60

To test this, we want to make `wantLayers` high enough to not cause a memory on its own but still trigger the machine-wide OOM when a slice gets create with the same length. On my local machine, it would take hours to create a slice of layers that fulfils that criteria, so instead I modify the Cosign production code to reflect a long list of manifests:

```golang
// Get implements oci.Signatures
func (s *sigs) Get() ([]oci.Signature, error) {
        m, err := s.Manifest()
        if err != nil {
                return nil, err
        }
        // Here we imitate a long list of manifests
        ms := make([]byte, 2600000000) // imitate a long list of manifests
        signatures := make([]oci.Signature, 0, len(ms))
        panic("Done")
        //signatures := make([]oci.Signature, 0, len(m.Layers))
        for _, desc := range m.Layers {
```

With this modified code, if we can cause an OOM without triggering the `panic("Done")`, we have succeeded.

## References
- https://github.com/sigstore/cosign/security/advisories/GHSA-95pr-fxf5-86gv
- https://nvd.nist.gov/vuln/detail/CVE-2024-29903
- https://github.com/sigstore/cosign/commit/629f5f8fa672973503edde75f84dcd984637629e
- https://github.com/sigstore/cosign
- https://github.com/sigstore/cosign/blob/14795db16417579fac0c00c11e166868d7976b61/pkg/cosign/verify.go#L948-L955
- https://github.com/sigstore/cosign/blob/286a98a4a99c1b2f32f84b0d560e324100312280/pkg/oci/remote/signatures.go#L56-L70
- https://github.com/sigstore/cosign/releases/tag/v2.2.4
