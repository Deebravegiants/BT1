# [M] SSRF vulnerability in jupyter-server-proxy

## Summary
Severity: Medium
Advisory: GHSA-gcv9-6737-pjqw
CVE: CVE-2022-21697
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-gcv9-6737-pjqw
Type: github-advisory

## Affected
- PyPI: `jupyter-server-proxy` — affected >=0 <3.2.1

## Details
### Impact

**What kind of vulnerability is it?**  Server-Side Request Forgery ( SSRF )

**Who is impacted?** Any user deploying Jupyter Server or Notebook with jupyter-proxy-server extension enabled. 

A lack of input validation allowed authenticated clients to proxy requests to other hosts, bypassing the `allowed_hosts` check. Because authentication is required, which already grants permissions to make the same requests via kernel or terminal execution, this is considered low to moderate severity.


### Patches

_Has the problem been patched? What versions should users upgrade to?_

Upgrade to 3.2.1, or apply the patch https://github.com/jupyterhub/jupyter-server-proxy/compare/v3.2.0...v3.2.1.patch

### For more information

If you have any questions or comments about this advisory:

* Open a topic [on our forum](https://discourse.jupyter.org)
* Email the Jupyter security team at [security@ipython.org](mailto:security@ipython.org)

## References
- https://github.com/jupyterhub/jupyter-server-proxy/security/advisories/GHSA-gcv9-6737-pjqw
- https://nvd.nist.gov/vuln/detail/CVE-2022-21697
- https://github.com/jupyterhub/jupyter-server-proxy/commit/fd31930bacd12188c448c886e0783529436b99eb
- https://github.com/jupyterhub/jupyter-server-proxy
- https://github.com/jupyterhub/jupyter-server-proxy/compare/v3.2.0...v3.2.1.patch
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server-proxy/PYSEC-2022-16.yaml
