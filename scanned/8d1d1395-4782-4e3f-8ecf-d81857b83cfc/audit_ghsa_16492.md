# [M] jupyter-scheduler's endpoint is missing authentication

## Summary
Severity: Medium
Advisory: GHSA-v9g2-g7j4-4jxc
CVE: CVE-2024-28188
CWE: CWE-200, CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-v9g2-g7j4-4jxc
Type: github-advisory

## Affected
- PyPI: `jupyter-scheduler` — affected >=1.0.0 <1.1.6
- PyPI: `jupyter-scheduler` — affected >=1.2.0 <1.2.1
- PyPI: `jupyter-scheduler` — affected >=1.3.0 <1.8.2
- PyPI: `jupyter-scheduler` — affected >=2.0.0 <2.5.2

## Details
### Impact

`jupyter_scheduler` is missing an authentication check in Jupyter Server on an API endpoint (`GET /scheduler/runtime_environments`) which lists the names of the Conda environments on the server. In affected versions, `jupyter_scheduler` allows an unauthenticated user to obtain the list of Conda environment names on the server. This reveals any information that may be present in a Conda environment name.

This issue does **not** allow an unauthenticated third party to read, modify, or enter the Conda environments present on the server where `jupyter_scheduler` is running. This issue only reveals the list of Conda environment names.

Impacted versions: `>=1.0.0,<=1.1.5 ; ==1.2.0 ; >=1.3.0,<=1.8.1 ; >=2.0.0,<=2.5.1`

### Patches

* `jupyter-scheduler==1.1.6`
* `jupyter-scheduler==1.2.1`
* `jupyter-scheduler==1.8.2`
* `jupyter-scheduler==2.5.2`

### Workarounds

Server operators who are unable to upgrade can disable the `jupyter-scheduler` extension with:

```
jupyter server extension disable jupyter-scheduler
```

### References

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] Vulnerability reporting page: https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/jupyter-server/jupyter-scheduler/security/advisories/GHSA-v9g2-g7j4-4jxc
- https://nvd.nist.gov/vuln/detail/CVE-2024-28188
- https://github.com/jupyter-server/jupyter_server/pull/1392
- https://github.com/jupyter-server/jupyter-scheduler/commit/06435a2277bb2b8f441ec9cedafa474572b92c5d
- https://github.com/jupyter-server/jupyter-scheduler/commit/a621b386397280cc8ee5a208dca4607cb71cdd65
- https://github.com/jupyter-server/jupyter-scheduler/commit/d428ac871909444e175ba421bf8ab4980d6ebf9f
- https://github.com/jupyter-server/jupyter-scheduler/commit/f4137a779fdf0cc4a9688a42dd8c6e7ade60f044
- https://github.com/jupyter-server/jupyter-scheduler
