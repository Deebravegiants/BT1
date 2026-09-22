# [M] gosaml2 vulnerable to Denial Of Service Via Deflate Decompression Bomb

## Summary
Severity: Medium
Advisory: GHSA-6gc3-crp7-25w5
CVE: CVE-2023-26483
CWE: CWE-409
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-03-02
Source: https://github.com/advisories/GHSA-6gc3-crp7-25w5
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/gosaml2` — affected >=0 <0.9.0

## Details
### Impact
SAML Service Providers using this library for SAML authentication support are likely susceptible to Denial of Service attacks. A bug in this library enables attackers to craft a `deflate`-compressed request which will consume significantly more memory during processing than the size of the original request. This may eventually lead to memory exhaustion and the process being killed.

### Mitigation
The maximum compression ratio achievable with `deflate` is 1032:1, so by limiting the size of bodies passed to gosaml2, limiting the rate and concurrency of calls, and ensuring that lots of memory is available to the process it _may_ be possible to help Go's garbage collector "keep up".

Implementors are encouraged not to rely on this.

### Patches
This issue is addressed in v0.9.0

## References
- https://github.com/russellhaering/gosaml2/security/advisories/GHSA-6gc3-crp7-25w5
- https://nvd.nist.gov/vuln/detail/CVE-2023-26483
- https://github.com/russellhaering/gosaml2/commit/f9d66040241093e8702649baff50cc70d2c683c0
- https://github.com/russellhaering/gosaml2
- https://github.com/russellhaering/gosaml2/releases/tag/v0.9.0
- https://pkg.go.dev/vuln/GO-2023-1602
