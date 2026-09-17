# [H] Predictable SIF UUID Identifiers in github.com/sylabs/sif

## Summary
Severity: High
Advisory: GHSA-4gh8-x3vv-phhg
CVE: CVE-2021-29499
CWE: CWE-330, CWE-340
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-4gh8-x3vv-phhg
Type: github-advisory

## Affected
- Go: `github.com/sylabs/sif` — affected >=0 <1.2.3

## Details
### Impact

The `siftool new` command and [func siftool.New()](https://pkg.go.dev/github.com/sylabs/sif/pkg/siftool#New) produce predictable UUID identifiers due to insecure randomness in the version of the `github.com/satori/go.uuid` module used as a dependency.

### Patches

A patch is available in version >= v1.2.3 of the module. Users are encouraged to upgrade.

The patch is commit https://github.com/sylabs/sif/commit/193962882122abf85ff5f5bcc86404933e71c07d

### Workarounds
Users passing [CreateInfo struct](https://pkg.go.dev/github.com/sylabs/sif/pkg/sif#CreateInfo) should ensure the `ID` field is generated using a version of `github.com/satori/go.uuid` that is not vulnerable to this issue. Unfortunately, the latest tagged release is vulnerable to this issue. One way to obtain a non-vulnerable version is:

```
go get github.com/satori/go.uuid@75cca531ea763666bc46e531da3b4c3b95f64557
```

### References
* https://github.com/satori/go.uuid/issues/73

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github.com/sylabs/sif](https://github.com/sylabs/sif/issues/new)
* Email us at [security@sylabs.io](mailto:security@sylabs.io)

## References
- https://github.com/sylabs/sif/security/advisories/GHSA-4gh8-x3vv-phhg
- https://nvd.nist.gov/vuln/detail/CVE-2021-29499
- https://github.com/satori/go.uuid/issues/73
- https://github.com/sylabs/sif/commit/193962882122abf85ff5f5bcc86404933e71c07d
- https://github.com/sylabs/sif
