# [M] Helm vulnerable to denial of service through schema file

## Summary
Severity: Medium
Advisory: GHSA-67fx-wx78-jx33
CVE: CVE-2022-23526
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-67fx-wx78-jx33
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.10.3

## Details
Fuzz testing, by Ada Logics and sponsored by the CNCF, identified input to functions in the `_chartutil_` package that can cause a segmentation violation. Applications that use functions from the `_chartutil_` package in the Helm SDK can have a Denial of Service attack when they use this package and it panics.

### Impact

The `_chartutil_` package contains a parser that loads a JSON Schema validation file. For example, the Helm client when rendering a chart will validate its values with the schema file. The `_chartutil_` package parses the schema file and loads it into structures Go can work with. Some schema files can cause array data structures to be created causing a memory violation.

Applications that use the `_chartutil_` package in the Helm SDK to parse a schema file can suffer a Denial of Service when that input causes a panic that cannot be recovered from.

The Helm Client will panic with a schema file that causes a memory violation panic. Helm is not a long running service so the panic will not affect future uses of the Helm client.

### Patches

This issue has been resolved in 3.10.3. 

### Workarounds

SDK users can validate schema files that are correctly formatted before passing them to the `_chartutil_` functions.

### For more information

Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits

Disclosed by Ada Logics in a fuzzing audit sponsored by CNCF.

## References
- https://github.com/helm/helm/security/advisories/GHSA-67fx-wx78-jx33
- https://nvd.nist.gov/vuln/detail/CVE-2022-23526
- https://github.com/helm/helm/commit/bafafa8bb1b571b61d7a9528da8d40c307dade3d
- https://github.com/helm/helm
- https://pkg.go.dev/vuln/GO-2022-1166
