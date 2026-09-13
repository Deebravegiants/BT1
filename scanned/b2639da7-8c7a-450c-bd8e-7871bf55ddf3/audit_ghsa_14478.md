# [M] fieldpath's Paved.SetValue allows growing arrays up to arbitrary sizes in crossplane-runtime

## Summary
Severity: Medium
Advisory: GHSA-vfvj-3m3g-m532
CVE: CVE-2023-27483
CWE: CWE-20, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-13
Source: https://github.com/advisories/GHSA-vfvj-3m3g-m532
Type: github-advisory

## Affected
- Go: `github.com/crossplane/crossplane-runtime` — affected >=0.17.0 <0.19.2
- Go: `github.com/crossplane/crossplane-runtime` — affected >=0.6.0 <0.16.1

## Details
### Summary

Fuzz testing on `crossplane/crossplane`, by Ada Logics and sponsored by the CNCF, identified input to a function in the `fieldpath` package that can cause an out of memory panic. Applications that use the `Paved` type's `SetValue` method with user provided input without proper validation might use excessive amounts of memory and cause an out of memory panic.

### Details

In the `fieldpath` package, the `SetValue` method of the `Paved` type sets a value on the inner object according to the provided path, without validating it first. This allows setting values in slices at any specific index and the code will grow the target array up to the required size. The index is currently capped at max uint32 (4294967295) given how indexes are parsed,  but that is still an unnecessarily large value.

### Workaround

Users can parse and validate the path before passing it to the `SetValue` method of the `Paved` type, constraining the index size as deemed appropriate.

### Credits

Disclosed by Ada Logics in a fuzzing audit sponsored by CNCF.

## References
- https://github.com/crossplane/crossplane-runtime/security/advisories/GHSA-vfvj-3m3g-m532
- https://nvd.nist.gov/vuln/detail/CVE-2023-27483
- https://github.com/crossplane/crossplane-runtime/commit/53508a9f4374604db140dd8ab2fa52276441e738
- https://github.com/crossplane/crossplane-runtime/commit/f67177024d906aaf5e13ee7cd470b4e87a9fef40
- https://github.com/crossplane/crossplane-runtime
- https://pkg.go.dev/vuln/GO-2023-1623
