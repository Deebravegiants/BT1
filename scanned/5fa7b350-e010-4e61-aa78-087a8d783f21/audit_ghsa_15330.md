# [H] RobotsAndPencils go-saml authentication bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-6h53-q94j-348w
CVE: CVE-2023-48703
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-6h53-q94j-348w
Type: github-advisory

## Affected
- Go: `github.com/RobotsAndPencils/go-saml` — affected >=0

## Details
RobotsAndPencils go-saml, a SAML client library written in Go, contains an authentication bypass vulnerability in all known versions. This is due to how the `xmlsec1` command line tool is called internally to verify the signature of SAML assertions. When `xmlsec1` is used without defining the enabled key data, the origin of the public key for the signature verification is, unfortunately, not restricted. That means an attacker can sign the SAML assertions themselves and provide the required public key (e.g. an RSA key) directly embedded in the SAML token. Projects still using RobotsAndPencils/go-saml should move to another SAML library or alternatively remove support for SAML from their projects. The vulnerability can likely temporarily be fixed by forking the go-saml project and adding the command line argument `--enabled-key-data` and specifying a value such as `x509` or `raw-x509-cert` when calling the `xmlsec1` binary in the verify function. Please note that this workaround must be carefully tested before it can be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48703
- https://github.com/RobotsAndPencils/go-saml
- https://securitylab.github.com/advisories/GHSL-2023-121_go-saml__archived_
