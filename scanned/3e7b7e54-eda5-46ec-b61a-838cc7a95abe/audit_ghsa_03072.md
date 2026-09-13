# [H] Cloud Foundry Routing Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-5796-p3m6-9qj4
CVE: CVE-2019-11289
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-5796-p3m6-9qj4
Type: github-advisory

## Affected
- Go: `code.cloudfoundry.org/gorouter` — affected >=0 <0.0.0-20191101214924-b1b5c44e050f

## Details
Cloud Foundry Routing, all versions before 0.0.0-20191101214924-b1b5c44e050f, does not properly validate nonce input. A remote unauthorized malicious user could forge a route service request using an invalid nonce that will cause the Gorouter to crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11289
- https://github.com/cloudfoundry/gorouter/commit/b1b5c44e050f73b399b379ca63a42a2c5780a83f
- https://github.com/cloudfoundry/gorouter
- https://pkg.go.dev/vuln/GO-2021-0102
- https://www.cloudfoundry.org/blog/cve-2019-11289
