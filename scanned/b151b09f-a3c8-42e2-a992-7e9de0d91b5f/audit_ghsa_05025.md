# [C] golang.org/x/crypto vulnerable to auth bypass via unenforced @revoked status

## Summary
Severity: Critical
Advisory: GHSA-5cgq-3rg8-m6cv
CVE: CVE-2026-42508
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-5cgq-3rg8-m6cv
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
Previously, a revoked 'SignatureKey' belonging to a CA was not correctly checked for revocation. Now, both the 'key' and 'key.SignatureKey' are checked for @revoked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42508
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42508.json
- https://pkg.go.dev/vuln/GO-2026-5021
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://go.dev/issue/79568
- https://go.dev/cl/781220
- https://cs.opensource.google/go/x/crypto
- https://bugzilla.redhat.com/show_bug.cgi?id=2480688
- https://access.redhat.com/security/cve/CVE-2026-42508
- https://access.redhat.com/errata/RHSA-2026:41066
- https://access.redhat.com/errata/RHSA-2026:41064
- https://access.redhat.com/errata/RHSA-2026:41036
- https://access.redhat.com/errata/RHSA-2026:41031
- https://access.redhat.com/errata/RHSA-2026:41019
- https://access.redhat.com/errata/RHSA-2026:40945
- https://access.redhat.com/errata/RHSA-2026:40262
- https://access.redhat.com/errata/RHSA-2026:40138
- https://access.redhat.com/errata/RHSA-2026:40118
- https://access.redhat.com/errata/RHSA-2026:37387
- https://access.redhat.com/errata/RHSA-2026:37123
