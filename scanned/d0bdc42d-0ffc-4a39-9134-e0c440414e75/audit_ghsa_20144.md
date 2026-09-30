# [M] Helm vulnerable to denial of service through string value parsing

## Summary
Severity: Medium
Advisory: GHSA-6rx9-889q-vv2r
CVE: CVE-2022-23524
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-6rx9-889q-vv2r
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.10.3

## Details
Fuzz testing, by Ada Logics and sponsored by the CNCF, identified input to functions in the _strvals_ package that can cause a stack overflow. In Go, a stack overflow cannot be recovered from. Applications that use functions from the _strvals_ package in the Helm SDK can have a Denial of Service attack when they use this package and it panics.

### Impact

The _strvals_ package contains a parser that turns strings into Go structures. For example, the Helm client has command line flags like `--set`, `--set-string`, and others that enable the user to pass in strings that are merged into the values. The _strvals_ package converts these strings into structures Go can work with. Some string inputs can cause array data structures to be created causing a stack overflow.

Applications that use the _strvals_ package in the Helm SDK to parse user supplied input can suffer a Denial of Service when that input causes a panic that cannot be recovered from.

The Helm Client will panic with input to `--set`, `--set-string`, and other value setting flags that causes a stack overflow. Helm is not a long running service so the panic will not affect future uses of the Helm client.

### Patches

This issue has been resolved in 3.10.3. 

### Workarounds

SDK users can validate strings supplied by users won't create large arrays causing significant memory usage before passing them to the _strvals_ functions.

### For more information

Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits

Disclosed by Ada Logics in a fuzzing audit sponsored by CNCF.

## References
- https://github.com/helm/helm/security/advisories/GHSA-6rx9-889q-vv2r
- https://nvd.nist.gov/vuln/detail/CVE-2022-23524
- https://github.com/helm/helm/commit/3636f6824757ff734cb265b8770efe48c1fb3737
- https://github.com/helm/helm
- https://pkg.go.dev/vuln/GO-2022-1167
