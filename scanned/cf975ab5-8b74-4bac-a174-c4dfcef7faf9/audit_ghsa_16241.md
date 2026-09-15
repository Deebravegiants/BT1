# [H] Boundary vulnerable to session hijacking through TLS certificate tampering

## Summary
Severity: High
Advisory: GHSA-vh73-q3rw-qx7w
CVE: CVE-2024-1052
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-05
Source: https://github.com/advisories/GHSA-vh73-q3rw-qx7w
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/boundary` — affected >=0.8.0 <0.15.0

## Details
Boundary and Boundary Enterprise (“Boundary”) is vulnerable to session hijacking through TLS certificate tampering. An attacker with privileges to enumerate active or pending sessions, obtain a private key pertaining to a session, and obtain a valid trust on first use (TOFU) token may craft a TLS certificate to hijack an active session and gain access to the underlying service or application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1052
- https://discuss.hashicorp.com/t/hcsec-2024-02-boundary-vulnerable-to-session-hijacking-through-tls-certificate-tampering/62458
- https://github.com/hashicorp/boundary
