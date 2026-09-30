# [M] Moby (Docker Engine) is vulnerable to Ambiguous OCI manifest parsing

## Summary
Severity: Medium
Advisory: GHSA-xmmx-7jpf-fx42
Ecosystem: Go
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-xmmx-7jpf-fx42
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <20.10.11
- Go: `github.com/moby/moby` — affected >=0 <20.10.11

## Details
### Impact
In the OCI Distribution Specification version 1.0.0 and prior and in the OCI Image Specification version 1.0.1 and prior, manifest and index documents are ambiguous without an accompanying Content-Type HTTP header.  Versions of Moby (Docker Engine) prior to 20.10.11 treat the Content-Type header as trusted and deserialize the document according to that header.  If the Content-Type header changed between pulls of the same ambiguous document (with the same digest), the document may be interpreted differently, meaning that the digest alone is insufficient to unambiguously identify the content of the image.

### Patches
This issue has been fixed in Moby (Docker Engine) 20.10.11.  Image pulls for manifests that contain a “manifests” field or indices which contain a “layers” field are rejected.

### Workarounds
Ensure you only pull images from trusted sources.

### References
https://github.com/opencontainers/distribution-spec/security/advisories/GHSA-mc8v-mgrf-8f4m
https://github.com/opencontainers/image-spec/security/advisories/GHSA-77vh-xpmg-72qh

### For more information
If you have any questions or comments about this advisory:
* [Open an issue in](https://github.com/moby/moby/issues/new)
* Email us at [security@docker.com](mailto:security@docker.com)

## References
- https://github.com/moby/moby/security/advisories/GHSA-xmmx-7jpf-fx42
