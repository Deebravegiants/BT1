# [C] Jupyter Server Proxy has a reflected XSS issue in host parameter

## Summary
Severity: Critical
Advisory: GHSA-fvcq-4x64-hqxr
CVE: CVE-2024-35225
CWE: CWE-116, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-11
Source: https://github.com/advisories/GHSA-fvcq-4x64-hqxr
Type: github-advisory

## Affected
- PyPI: `jupyter-server-proxy` — affected >=3.0.0 <3.2.4
- PyPI: `jupyter-server-proxy` — affected >=4.0.0 <4.2.0

## Details
### Impact

There is a reflected cross-site scripting (XSS) issue in `jupyter-server-proxy`[1]. The `/proxy` endpoint accepts a `host` path segment in the format `/proxy/<host>`. When this endpoint is called with an invalid `host` value, `jupyter-server-proxy` replies with a response that includes the value of `host`, without sanitization [2]. A third-party actor can leverage this by sending a phishing link with an invalid `host` value containing custom JavaScript to a user. When the user clicks this phishing link, the browser renders the response of `GET /proxy/<host>`, which runs the custom JavaScript contained in `host` set by the actor.
As any arbitrary JavaScript can be run after the user clicks on a phishing link, this issue permits extensive access to the user's JupyterLab instance for an actor. This issue exists in the latest release of `jupyter-server-proxy`, currently `v4.1.2`.
**Impacted versions:** `>=3.0.0,<=4.1.2`

### Patches

The patches are included in `==4.2.0` and `==3.2.4`.

### Workarounds

Server operators who are unable to upgrade can disable the `jupyter-server-proxy` extension with:

```
jupyter server extension disable jupyter-server-proxy
```

### References

[1] : https://github.com/jupyterhub/jupyter-server-proxy/
[2] : https://github.com/jupyterhub/jupyter-server-proxy/blob/62a290f08750f7ae55a0c29ca339c9a39a7b2a7b/jupyter_server_proxy/handlers.py#L328

## References
- https://github.com/jupyterhub/jupyter-server-proxy/security/advisories/GHSA-fvcq-4x64-hqxr
- https://nvd.nist.gov/vuln/detail/CVE-2024-35225
- https://github.com/jupyterhub/jupyter-server-proxy/commit/7abc9dc5bbb0b4b440548a5375261b8b8192fc22
- https://github.com/jupyterhub/jupyter-server-proxy/commit/ff78128087e73fb9d0909e1366f8bf051e8ea878
- https://github.com/jupyterhub/jupyter-server-proxy
- https://github.com/jupyterhub/jupyter-server-proxy/blob/62a290f08750f7ae55a0c29ca339c9a39a7b2a7b/jupyter_server_proxy/handlers.py#L328
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server-proxy/PYSEC-2024-236.yaml
