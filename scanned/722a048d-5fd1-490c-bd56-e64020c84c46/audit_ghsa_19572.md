# [C] TigerVNC accessible via the network and not just via a UNIX socket as intended

## Summary
Severity: Critical
Advisory: GHSA-vrq4-9hc3-cgp7
CVE: CVE-2025-32428
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-04-12
Source: https://github.com/advisories/GHSA-vrq4-9hc3-cgp7
Type: github-advisory

## Affected
- PyPI: `jupyter-remote-desktop-proxy` — affected >=3.0.0 <3.0.1

## Details
## Summary

`jupyter-remote-desktop-proxy` was meant to rely on UNIX sockets readable only by the current user since version 3.0.0, but when used with TigerVNC, the VNC server started by `jupyter-remote-desktop-proxy` were still accessible via the network.

This vulnerability does not affect users having TurboVNC as the `vncserver` executable.

## Credits

This vulnerability was identified by Arne Gottwald at University of Göttingen and analyzed, reported, and reviewed by @frejanordsiek.

## References
- https://github.com/jupyterhub/jupyter-remote-desktop-proxy/security/advisories/GHSA-vrq4-9hc3-cgp7
- https://nvd.nist.gov/vuln/detail/CVE-2025-32428
- https://github.com/jupyterhub/jupyter-remote-desktop-proxy/commit/7dd54c25a4253badd8ea68895437e5a66a59090d
- https://github.com/jupyterhub/jupyter-remote-desktop-proxy
