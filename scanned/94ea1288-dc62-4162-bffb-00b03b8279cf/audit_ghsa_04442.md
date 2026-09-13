# [H] golang.org/x/crypto: Invoking pathological RSA/DSA parameters may cause DoS

## Summary
Severity: High
Advisory: GHSA-w879-237q-wc7r
CVE: CVE-2026-39829
CWE: CWE-1284, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-w879-237q-wc7r
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
The RSA and DSA public key parsers did not enforce size limits on key parameters. A crafted public key with an excessively large modulus or DSA parameter could cause several minutes of CPU consumption during signature verification. This could be triggered by unauthenticated clients during public key authentication. RSA moduli are now limited to 8192 bits, and DSA parameters are validated per FIPS 186-2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39829
- https://access.redhat.com/errata/RHSA-2026:37387
- https://access.redhat.com/errata/RHSA-2026:40118
- https://access.redhat.com/errata/RHSA-2026:40119
- https://access.redhat.com/errata/RHSA-2026:40262
- https://access.redhat.com/errata/RHSA-2026:40945
- https://access.redhat.com/errata/RHSA-2026:40969
- https://access.redhat.com/errata/RHSA-2026:40972
- https://access.redhat.com/errata/RHSA-2026:40974
- https://access.redhat.com/errata/RHSA-2026:41019
- https://access.redhat.com/errata/RHSA-2026:41031
- https://access.redhat.com/errata/RHSA-2026:41036
- https://access.redhat.com/errata/RHSA-2026:41055
- https://access.redhat.com/errata/RHSA-2026:41066
- https://access.redhat.com/security/cve/CVE-2026-39829
- https://bugzilla.redhat.com/show_bug.cgi?id=2480681
- https://cs.opensource.google/go/x/crypto
- https://go.dev/cl/781641
- https://go.dev/cl/781661
- https://go.dev/issue/79565
