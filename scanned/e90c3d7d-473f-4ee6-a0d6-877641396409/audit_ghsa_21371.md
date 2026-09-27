# [M] SIF's Digital Signature Hash Algorithms Not Validated

## Summary
Severity: Medium
Advisory: GHSA-m5m3-46gj-wch8
CVE: CVE-2022-39237
CWE: CWE-327, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-m5m3-46gj-wch8
Type: github-advisory

## Affected
- Go: `github.com/sylabs/sif/v2` — affected >=0 <2.8.1

## Details
### Impact

The `github.com/sylabs/sif/v2/pkg/integrity` package does not verify that the hash algorithm(s) used are cryptographically secure when verifying digital signatures.

### Patches

A patch is available in version >= v2.8.1 of the module. Users are encouraged to upgrade.

The patch is commit https://github.com/sylabs/sif/commit/07fb86029a12e3210f6131e065570124605daeaa

### Workarounds

Users may independently validate that the hash algorithm(s) used for metadata digest(s) and signature hash are cryptographically secure.

### References

* [CVE-2004-2761](https://nvd.nist.gov/vuln/detail/cve-2004-2761)
* [CVE-2005-4900](https://nvd.nist.gov/vuln/detail/cve-2005-4900)

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [github.com/sylabs/sif](https://github.com/sylabs/sif/issues/new)
* Email us at [security@sylabs.io](mailto:security@sylabs.io)

## References
- https://github.com/sylabs/sif/security/advisories/GHSA-m5m3-46gj-wch8
- https://nvd.nist.gov/vuln/detail/CVE-2022-39237
- https://github.com/sylabs/sif/commit/07fb86029a12e3210f6131e065570124605daeaa
- https://github.com/sylabs/sif
- https://github.com/sylabs/sif/releases/tag/v2.8.1
- https://nvd.nist.gov/vuln/detail/cve-2004-2761
- https://nvd.nist.gov/vuln/detail/cve-2005-4900
- https://pkg.go.dev/vuln/GO-2022-1045
- https://security.gentoo.org/glsa/202210-19
