# [M] OCI image importer memory exhaustion in github.com/containerd/containerd

## Summary
Severity: Medium
Advisory: GHSA-259w-8hf6-59c2
CVE: CVE-2023-25153
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-259w-8hf6-59c2
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.5.18
- Go: `github.com/containerd/containerd` — affected >=1.6.0 <1.6.18

## Details
### Impact
When importing an OCI image, there was no limit on the number of bytes read for certain files. A maliciously crafted image with a large file where a limit was not applied could cause a denial of service.

### Patches

This bug has been fixed in containerd 1.6.18 and 1.5.18.  Users should update to these versions to resolve the issue.

### Workarounds

Ensure that only trusted images are used and that only trusted users have permissions to import images. 

### Credits

The containerd project would like to thank [David Korczynski](https://github.com/DavidKorczynski) and [Adam Korczynski](https://github.com/AdamKorcz) of ADA Logics for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md) during a security fuzzing audit sponsored by CNCF.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-259w-8hf6-59c2
- https://nvd.nist.gov/vuln/detail/CVE-2023-25153
- https://github.com/containerd/containerd/commit/0c314901076a74a7b797a545d2f462285fdbb8c4
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/releases/tag/v1.5.18
- https://github.com/containerd/containerd/releases/tag/v1.6.18
- https://pkg.go.dev/vuln/GO-2023-1573
