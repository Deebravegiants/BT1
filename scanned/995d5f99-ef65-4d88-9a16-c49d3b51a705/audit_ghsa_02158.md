# [H] Code injection in nbgitpuller

## Summary
Severity: High
Advisory: GHSA-mq5p-2mcr-m52j
CVE: CVE-2021-39160
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-mq5p-2mcr-m52j
Type: github-advisory

## Affected
- PyPI: `nbgitpuller` — affected >=0.9.0 <0.10.2

## Details
### Impact

Due to an unsanitized input, visiting maliciously crafted links could result in arbitrary code execution in the user environment.

### Patches

0.10.2

### Workarounds

None, other than upgrade to 0.10.2 or downgrade to 0.8.x.


### For more information

If you have any questions or comments about this advisory:

* Open an issue in [nbgitpuller](https://github.com/jupyterhub/nbgitpuller/issues)
* Email our security team at [security@ipython.org](mailto:security@ipython.org)

## References
- https://github.com/jupyterhub/nbgitpuller/security/advisories/GHSA-mq5p-2mcr-m52j
- https://nvd.nist.gov/vuln/detail/CVE-2021-39160
- https://github.com/jupyterhub/nbgitpuller/commit/07690644f29a566011dd0d7ba14cae3eb0490481
- https://github.com/jupyterhub/nbgitpuller
- https://github.com/jupyterhub/nbgitpuller/blob/main/CHANGELOG.md#0102---2021-08-25
- https://github.com/pypa/advisory-database/tree/main/vulns/nbgitpuller/PYSEC-2021-315.yaml
