# [M] JupyterHub has cross-origin form POSTs bypass XSRF (CWE-352)

## Summary
Severity: Medium
Advisory: GHSA-m68r-v472-jgq9
CVE: CVE-2026-40864
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-m68r-v472-jgq9
Type: github-advisory

## Affected
- PyPI: `jupyterhub` — affected >=4.1.0 <5.4.5

## Details
## Summary

JupyterHub's XSRF protection (updated in 4.1.0) inappropriately treated requests with `Sec-Fetch-Mode: no-cors` as same-origin requests, which they are not, bypassing XSRF checks. The JSON API is not affected, only HTTP form endpoints, such as `/hub/spawn` and `/hub/accept-share`, meaning attackers could trigger server spawn (but not access the server) and if the attacker is a JupyterHub user permitted to share access to their server, cause a user to accept a share and have access to the attacker's server.

## Patches

Upgrade to JupyterHub 5.4.5.

## Mitigations

If a reverse proxy is in use, drop requests to JupyterHub with `Sec-Fetch-Mode: no-cors`.

## References
- https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-m68r-v472-jgq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40864
- https://github.com/jupyterhub/jupyterhub/commit/9c5ec277d3cda5a59de2d8c8117efa77bd941127
- https://github.com/jupyterhub/jupyterhub
