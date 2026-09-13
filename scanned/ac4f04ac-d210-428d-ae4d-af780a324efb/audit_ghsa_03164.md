# [M] github.com/russellhaering/goxmldsig vulnerable to Signature Validation Bypass

## Summary
Severity: Medium
Advisory: GHSA-q547-gmf8-8jr7
CVE: CVE-2020-15216
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-q547-gmf8-8jr7
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/goxmldsig` — affected >=0 <1.1.0

## Details
### Impact
With a carefully crafted XML file, an attacker can completely bypass signature validation and pass off an altered file as a signed one. 

### Patches
A patch is available, all users of goxmldsig should upgrade to v1.1.0.

### For more information
If you have any questions or comments about this advisory open an issue at https://github.com/russellhaering/goxmldsig

## References
- https://github.com/russellhaering/goxmldsig/security/advisories/GHSA-q547-gmf8-8jr7
- https://nvd.nist.gov/vuln/detail/CVE-2020-15216
- https://github.com/russellhaering/goxmldsig/commit/f6188febf0c29d7ffe26a0436212b19cb9615e64
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GUH33FPUXED3FHYL25BJOQPRKFGPOMS2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZECBFD4M4PHBMBOCMSQ537NOU37QOVWP
- https://pkg.go.dev/github.com/russellhaering/goxmldsig?tab=overview
- https://pkg.go.dev/vuln/GO-2020-0050
