# [M] LTI JupyterHub Authenticator: Unbounded Memory Growth via Nonce Storage (Denial of Service)

## Summary
Severity: Medium
Advisory: GHSA-8mxq-7xr7-2fxj
CVE: CVE-2026-34052
CWE: CWE-401, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-8mxq-7xr7-2fxj
Type: github-advisory

## Affected
- PyPI: `jupyterhub-ltiauthenticator` — affected >=0 <1.6.3

## Details
## Summary

The LTI 1.1 validator stores OAuth nonces in a class-level dictionary that grows without bounds. Nonces are added before signature validation, so an attacker with knowledge of a valid consumer key can send repeated requests with unique nonces to gradually exhaust server memory, causing a denial of service.

## Patches

- upgrade jupyterhub-litauthenticator to 1.6.3

## References
- https://github.com/jupyterhub/ltiauthenticator/security/advisories/GHSA-8mxq-7xr7-2fxj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34052
- https://github.com/jupyterhub/ltiauthenticator
- https://github.com/jupyterhub/ltiauthenticator/releases/tag/1.6.3
