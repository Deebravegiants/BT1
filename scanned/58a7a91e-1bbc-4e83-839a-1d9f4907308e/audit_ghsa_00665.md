# [M] Jupyter Server open redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9f66-54xg-pc2c
CVE: CVE-2020-26275
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-12-21
Source: https://github.com/advisories/GHSA-9f66-54xg-pc2c
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <1.1.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Open redirect vulnerability - a maliciously crafted link to a jupyter server could redirect the browser to a different website.

All jupyter servers running without a base_url prefix are technically affected, however, these maliciously crafted links can only be reasonably made for known jupyter server hosts. A link to your jupyter server may *appear* safe, but ultimately redirect to a spoofed server on the public internet. This same vulnerability was patched in upstream notebook v5.7.8.

### Patches

_Has the problem been patched? What versions should users upgrade to?_

Patched in jupyter_server 1.1.1. If upgrade is not available, a workaround can be to run your server on a url prefix:

```
jupyter server --ServerApp.base_url=/jupyter/
```

### References

[OWASP page on open redirects](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)

### For more information

If you have any questions or comments about this advisory, or vulnerabilities to report, please email our security list [security@ipython.org](mailto:security@ipython.org).

Credit: Yaniv Nizry from CxSCA group at Checkmarx

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-9f66-54xg-pc2c
- https://nvd.nist.gov/vuln/detail/CVE-2020-26275
- https://github.com/jupyter-server/jupyter_server/commit/85e4abccf6ea9321d29153f73b0bd72ccb3a6bca
- https://advisory.checkmarx.net/advisory/CX-2020-4291
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2020-346.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2020-50.yaml
- https://pypi.org/project/jupyter-server
