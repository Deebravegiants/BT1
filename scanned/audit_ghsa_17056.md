# [H] Cross site scripting (XSS) in JupyterHub via Self-XSS leveraged by Cookie Tossing

## Summary
Severity: High
Advisory: GHSA-7r3h-4ph8-w38g
CVE: CVE-2024-28233
CWE: CWE-352, CWE-565, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-28
Source: https://github.com/advisories/GHSA-7r3h-4ph8-w38g
Type: github-advisory

## Affected
- PyPI: `jupyterhub` — affected >=0 <4.1.0

## Details
### Impact

Affected configurations:

- Single-origin JupyterHub deployments
- JupyterHub deployments with user-controlled applications running on subdomains or peer subdomains of either the Hub or a single-user server.

By tricking a user into visiting a malicious subdomain, the attacker can achieve an XSS directly affecting the former's session. More precisely, in the context of JupyterHub, this XSS could achieve the following:

- Full access to JupyterHub API and user's single-user server, e.g.
  - Create and exfiltrate an API Token
  - Exfiltrate all files hosted on the user's single-user server: notebooks, images, etc.
  - Install malicious extensions. They can be used as a backdoor to silently regain access to victim's session anytime.

### Patches

To prevent cookie-tossing:

- Upgrade to JupyterHub 4.1 (both hub and user environment)
- enable per-user domains via `c.JupyterHub.subdomain_host = "https://mydomain.example.org"`
- set `c.JupyterHub.cookie_host_prefix_enabled = True` to enable domain-locked cookies

or, if available (applies to earlier JupyterHub versions):

- deploy jupyterhub on its own domain, not shared with any other services
- enable per-user domains via `c.JupyterHub.subdomain_host = "https://mydomain.example.org"`

## References
- https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-7r3h-4ph8-w38g
- https://nvd.nist.gov/vuln/detail/CVE-2024-28233
- https://github.com/jupyterhub/jupyterhub/commit/e2798a088f5ad45340fe79cdf1386198e664f77f
- https://github.com/jupyterhub/jupyterhub
