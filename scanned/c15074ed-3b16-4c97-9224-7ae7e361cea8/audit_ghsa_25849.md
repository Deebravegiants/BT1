# [H] Insertion of Sensitive Information into Log File in Jupyter notebook

## Summary
Severity: High
Advisory: GHSA-p737-p57g-4cpr
CVE: CVE-2022-24757
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-25
Source: https://github.com/advisories/GHSA-p737-p57g-4cpr
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <1.15.4

## Details
### Impact
_What kind of vulnerability is it?_

Anytime a 5xx error is triggered, the auth cookie and other header values are recorded in Jupyter Server logs by default. Considering these logs do not require root access, an attacker can monitor these logs, steal sensitive auth/cookie information, and gain access to the Jupyter server.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Upgrade to Jupyter Server version 1.15.4

### For more information

If you have any questions or comments about this advisory, or vulnerabilities to report, please email our security list [security@ipython.org](mailto:security@ipython.org).

Credit: @3coins for reporting. Thank you!

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-p737-p57g-4cpr
- https://nvd.nist.gov/vuln/detail/CVE-2022-24757
- https://github.com/jupyter-server/jupyter_server/commit/a5683aca0b0e412672ac6218d09f74d44ca0de5a
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2022-179.yaml
