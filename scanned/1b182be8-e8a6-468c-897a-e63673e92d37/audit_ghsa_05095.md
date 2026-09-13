# [C] golang.org/x/crypto doesn't enforce invoking key constraints

## Summary
Severity: Critical
Advisory: GHSA-jppx-rxg9-jmrx
CVE: CVE-2026-39833
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-jppx-rxg9-jmrx
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
The in-memory keyring returned by NewKeyring() silently accepted keys with the ConfirmBeforeUse constraint but never enforced it. The key would sign without any confirmation prompt, with no indication to the caller that the constraint was not in effect. NewKeyring() now returns an error when unsupported constraints are requested.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39833
- https://cs.opensource.google/go/x/crypto
- https://go.dev/cl/778640
- https://go.dev/cl/778641
- https://go.dev/issue/79436
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://pkg.go.dev/vuln/GO-2026-5005
