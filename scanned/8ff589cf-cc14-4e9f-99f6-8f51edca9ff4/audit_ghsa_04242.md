# [C] golang.org/x/crypto: Invoking VerifiedPublicKeyCallback permissions skip enforcement

## Summary
Severity: Critical
Advisory: GHSA-x527-x647-q7gg
CVE: CVE-2026-46595
CWE: CWE-303, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-x527-x647-q7gg
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
Previously, CVE-2024-45337 fixed an authorization bypass for misused ssh server configurations; if any other type of callback is passed other than public key, then the source-address validation would be skipped.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46595
- https://nvd.nist.gov/vuln/detail/CVE-2024-45337
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46595.json
- https://pkg.go.dev/vuln/GO-2026-5023
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://go.dev/issue/79570
- https://go.dev/cl/781642
- https://cs.opensource.google/go/x/crypto
- https://bugzilla.redhat.com/show_bug.cgi?id=2480689
- https://access.redhat.com/security/cve/CVE-2026-46595
- https://access.redhat.com/errata/RHSA-2026:41036
- https://access.redhat.com/errata/RHSA-2026:41019
- https://access.redhat.com/errata/RHSA-2026:40945
- https://access.redhat.com/errata/RHSA-2026:40118
- https://access.redhat.com/errata/RHSA-2026:37387
- https://access.redhat.com/errata/RHSA-2026:37275
- https://access.redhat.com/errata/RHSA-2026:36820
- https://access.redhat.com/errata/RHSA-2026:36808
- https://access.redhat.com/errata/RHSA-2026:36797
- https://access.redhat.com/errata/RHSA-2026:36796
