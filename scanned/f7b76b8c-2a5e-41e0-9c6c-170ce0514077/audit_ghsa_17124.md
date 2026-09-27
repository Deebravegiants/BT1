# [H] Memory leaks in code encrypting and verifying RSA payloads

## Summary
Severity: High
Advisory: GHSA-78hx-gp6g-7mj6
CVE: CVE-2024-1394
CWE: CWE-400, CWE-401
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-78hx-gp6g-7mj6
Type: github-advisory

## Affected
- Go: `github.com/golang-fips/go` — affected >=0
- Go: `github.com/golang-fips/openssl/v2` — affected >=0 <2.0.1
- Go: `github.com/microsoft/go-crypto-openssl` — affected >=0
- Go: `github.com/microsoft/go-crypto-openssl/openssl` — affected >=0 <0.2.9

## Details
Using crafted public RSA keys which are not compliant with SP 800-56B can cause a small memory leak when encrypting and verifying payloads.

An attacker can leverage this flaw to gradually erode available memory to the point where the host crashes for lack of resources. Upon restart the attacker would have to begin again, but nevertheless there is the potential to deny service.

## References
- https://github.com/golang-fips/openssl/security/advisories/GHSA-78hx-gp6g-7mj6
- https://nvd.nist.gov/vuln/detail/CVE-2024-1394
- https://github.com/microsoft/go-crypto-openssl/commit/104fe7f6912788d2ad44602f77a0a0a62f1f259f
- https://github.com/golang-fips/openssl/commit/85d31d0d257ce842c8a1e63c4d230ae850348136
- https://access.redhat.com/errata/RHSA-2024:1462
- https://access.redhat.com/errata/RHSA-2024:4378
- https://access.redhat.com/errata/RHSA-2024:4379
- https://access.redhat.com/errata/RHSA-2024:4502
- https://access.redhat.com/errata/RHSA-2024:4581
- https://access.redhat.com/errata/RHSA-2024:4591
- https://access.redhat.com/errata/RHSA-2024:4672
- https://access.redhat.com/errata/RHSA-2024:4699
- https://access.redhat.com/errata/RHSA-2024:4761
- https://access.redhat.com/errata/RHSA-2024:4762
- https://access.redhat.com/errata/RHSA-2024:4960
- https://access.redhat.com/errata/RHSA-2024:5258
- https://access.redhat.com/errata/RHSA-2024:5634
- https://access.redhat.com/errata/RHSA-2024:7262
- https://access.redhat.com/security/cve/CVE-2024-1394
- https://bugzilla.redhat.com/show_bug.cgi?id=2262921
