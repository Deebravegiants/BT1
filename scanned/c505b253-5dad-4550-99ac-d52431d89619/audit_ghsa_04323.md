# [C] Jupyter Server: Stored XSS in `NbconvertFileHandler` / `NbconvertPostHandler` via missing `sandbox` CSP 

## Summary
Severity: Critical
Advisory: GHSA-fcw5-x6j4-ccmp
CVE: CVE-2026-44727
CWE: CWE-1021, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-fcw5-x6j4-ccmp
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <2.20.0

## Details
The nbconvert HTTP handlers in jupyter_server render user-authored notebook HTML under the Jupyter origin without a sandbox directive in their `Content-Security-Policy`. 

Combined with `nbconvert.HTMLExporter`'s default non-sanitizing behavior, a notebook carrying an HTML payload in a display_data output triggers stored XSS with cookie access, full /api/* authority, and kernel RCE.

### Impact

An authenticated victim who navigates to `/nbconvert/html/<path>` containing attacker-authored output can have their token exfiltrated to another domain because it is executed in the Jupyter origin.

### Patches

Fixed in v2.20.0, commit [6cbee8d](https://github.com/jupyter-server/jupyter_server/commit/6cbee8d65e71abac851c4492fea987ad080580bd)


### Workarounds

For deployments where editing the installed jupyter_server is impractical (containerized builds, read-only images), adding this to jupyter_server_config.py has the same effect as the patch above without touching source files:

```
import jupyter_server.nbconvert.handlers as _nb

def _csp(self):
    return super(type(self), self).content_security_policy + "; sandbox allow-scripts"

_nb.NbconvertFileHandler.content_security_policy = property(_csp)
_nb.NbconvertPostHandler.content_security_policy = property(_csp)
```

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-fcw5-x6j4-ccmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-44727
- https://github.com/jupyter-server/jupyter_server/commit/6cbee8d65e71abac851c4492fea987ad080580bd
- https://access.redhat.com/errata/RHSA-2026:43038
- https://access.redhat.com/errata/RHSA-2026:60520
- https://access.redhat.com/security/cve/CVE-2026-44727
- https://bugzilla.redhat.com/show_bug.cgi?id=2491516
- https://github.com/advisories/GHSA-fcw5-x6j4-ccmp
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2026-366.yaml
- https://pypi.org/project/jupyter-server
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44727.json
