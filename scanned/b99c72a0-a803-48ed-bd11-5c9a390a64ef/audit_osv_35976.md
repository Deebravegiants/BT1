# [M] Unauthenticated SSRF in PIA via OIDC issuer allowlist bypass

## Summary
Severity: Medium
Advisory: CVE-2026-18353
Aliases: GHSA-v249-9xjm-qhgf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-18353
Type: osv

## Details
PIA's `POST /v1/upload/sbom` endpoint accepts a Bearer JWT and checks its **unverified** `iss` claim against an issuer allowlist using Python's `urlparse` before performing OIDC discovery with `requests`. Because `urlparse` and `requests`/`urllib3` parse an authority string containing a backslash (e.g. `https://attacker-host\@ci.eclipse.org/`) into *different* hostnames, an attacker can craft an issuer that passes the allowlist check yet drives `requests` — and subsequently `urllib.request.urlopen` for JWKS retrieval — to connect to an arbitrary attacker-chosen host, port, and scheme.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18353.json
- https://github.com/eclipse-csi/pia/security/advisories/GHSA-v249-9xjm-qhgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-18353
- https://github.com/eclipse-csi/pia
