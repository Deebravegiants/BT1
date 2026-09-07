# [M] KubeVela VelaUX APIserver has SSRF vulnerability 

## Summary
Severity: Medium
Advisory: GHSA-m5xf-x7q6-3rm7
CVE: CVE-2022-39383
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-18
Source: https://github.com/advisories/GHSA-m5xf-x7q6-3rm7
Type: github-advisory

## Affected
- Go: `github.com/oam-dev/kubevela` — affected >=1.6.0-alpha.1 <1.6.2
- Go: `github.com/oam-dev/kubevela` — affected >=0 <1.5.9

## Details
### Impact
Users using the VelaUX APIServer could be affected by this vulnerability.

When using Helm Chart as the component delivery method, the request address of the warehouse is not restricted, and there is a blind SSRF vulnerability.

This issue is patched in 1.5.9 and 1.6.2.

### References
Fix by: #5000 

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [KubeVela repo](https://github.com/kubevela/kubevela)
* Email us at [here](https://github.com/kubevela/kubevela#contact-us)

## References
- https://github.com/kubevela/kubevela/security/advisories/GHSA-m5xf-x7q6-3rm7
- https://nvd.nist.gov/vuln/detail/CVE-2022-39383
- https://github.com/kubevela/kubevela/pull/5000
- https://github.com/kubevela/kubevela
- https://pkg.go.dev/vuln/GO-2022-1113
