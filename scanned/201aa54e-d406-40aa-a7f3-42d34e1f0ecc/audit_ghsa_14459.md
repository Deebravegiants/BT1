# [H] nistec has Incorrect Calculation in Multiplication of unreduced P-256 scalars

## Summary
Severity: High
Advisory: GHSA-f6hc-9g49-xmx7
CVE: CVE-2023-24533
CWE: CWE-682
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-f6hc-9g49-xmx7
Type: github-advisory

## Affected
- Go: `filippo.io/nistec` — affected >=0 <0.0.2

## Details
Multiplication of certain unreduced P-256 scalars produce incorrect results. There are no protocols known at this time that can be attacked due to this.

From the fix commit notes:

> Unlike the rest of nistec, the P-256 assembly doesn't use complete addition formulas, meaning that p256PointAdd[Affine]Asm won't return the correct value if the two inputs are equal.
> 
> This was (undocumentedly) ignored in the scalar multiplication loops because as long as the input point is not the identity and the scalar is lower than the order of the group, the addition inputs can't be the same.
> 
> As part of the math/big rewrite, we went however from always reducing the scalar to only checking its length, under the incorrect assumption that the scalar multiplication loop didn't require reduction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24533
- https://github.com/FiloSottile/nistec/commit/c58aa1223ccf3943513e1e661cebce95af137244
- https://github.com/FiloSottile/nistec
- https://go.dev/issue/58647
- https://pkg.go.dev/vuln/GO-2023-1595
