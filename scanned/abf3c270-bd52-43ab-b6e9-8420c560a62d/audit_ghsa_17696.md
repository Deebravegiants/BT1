# [H] nbgrader's `frame-ancestors: self` grants all users access to formgrader

## Summary
Severity: High
Advisory: GHSA-fcr8-4r9f-r66m
CVE: CVE-2025-23205
CWE: CWE-1021, CWE-668
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-17
Source: https://github.com/advisories/GHSA-fcr8-4r9f-r66m
Type: github-advisory

## Affected
- PyPI: `nbgrader` — affected >=0.9.4 <0.9.5

## Details
### Impact

Enabling frame-ancestors: 'self' grants any JupyterHub user the ability to extract formgrader content by sending malicious links to users with access to formgrader, at least when using the default JupyterHub configuration of `enable_subdomains = False`.

#1915 disables a protection which would allow user Alice to craft a page embedding formgrader in an IFrame. If Bob visits that page, his credentials will be sent and the formgrader page loaded. Because Alice's page is on the same Origin as the formgrader iframe, Javasript on Alice's page has _full access_ to the contents of the page served by formgrader using Bob's credentials.

### Workarounds

- Disable `frame-ancestors: self`, or
- enable per-user and per-service subdomains with `JupyterHub.enable_subdomains = True` (then even if embedding in an IFrame is allowed, the host page does not have access to the contents of the frame).

### References

JupyterHub documentation on why and when `frame-ancestors: self` is insecure, and why it was disabled by default: https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html#:~:text=frame-ancestors

## References
- https://github.com/jupyter/nbgrader/security/advisories/GHSA-fcr8-4r9f-r66m
- https://nvd.nist.gov/vuln/detail/CVE-2025-23205
- https://github.com/jupyter/nbgrader/pull/1915
- https://github.com/jupyter/nbgrader/commit/73e137511ac1dc02e95790d4fd6d4d88dab42325
- https://github.com/jupyter/nbgrader
- https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html
