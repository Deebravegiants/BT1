# [H] JupyterLab vulnerable to potential authentication and CSRF tokens leak

## Summary
Severity: High
Advisory: GHSA-44cc-43rp-5947
CVE: CVE-2024-22421
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-01-19
Source: https://github.com/advisories/GHSA-44cc-43rp-5947
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=4.0.0 <4.0.11
- PyPI: `jupyterlab` — affected >=0 <3.6.7
- PyPI: `notebook` — affected >=7.0.0 <7.0.7

## Details
### Impact
Users of JupyterLab who click on a malicious link may get their `Authorization` and `XSRFToken` tokens exposed to a third party when running an older `jupyter-server` version.

### Patches
JupyterLab 4.1.0b2, 4.0.11, and 3.6.7 were patched.

### Workarounds
No workaround has been identified, however users should ensure to upgrade `jupyter-server` to version 2.7.2 or newer which includes a redirect vulnerability fix.

### References

Vulnerability reported by user @davwwwx via the [bug bounty program](https://app.intigriti.com/programs/jupyter/jupyter/detail) [sponsored by the European Commission](https://commission.europa.eu/news/european-commissions-open-source-programme-office-starts-bug-bounties-2022-01-19_en) and hosted on the [Intigriti platform](https://www.intigriti.com/).

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-44cc-43rp-5947
- https://nvd.nist.gov/vuln/detail/CVE-2024-22421
- https://github.com/jupyterlab/jupyterlab/commit/19bd9b96cb2e77170a67e43121637d0b5619e8c6
- https://github.com/jupyterlab/jupyterlab/commit/1ef7a4fa0202ebdf663e1cc0b45c8813a34a0b96
- https://github.com/jupyterlab/jupyterlab/commit/fccd83dc4441da0384ee3fd1322c3b2d9ad4caaa
- https://github.com/jupyterlab/jupyterlab
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UQJKNRDRFMKGVRIYNNN6CKMNJDNYWO2H
