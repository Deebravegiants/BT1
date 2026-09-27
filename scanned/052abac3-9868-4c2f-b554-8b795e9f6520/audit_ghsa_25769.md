# [C] Command injection in libvcs and vcspull

## Summary
Severity: Critical
Advisory: GHSA-mv2w-4jqc-6fg4
CVE: CVE-2022-21187
CWE: CWE-74, CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-15
Source: https://github.com/advisories/GHSA-mv2w-4jqc-6fg4
Type: github-advisory

## Affected
- PyPI: `libvcs` — affected >=0 <0.11.1
- PyPI: `vcspull` — affected >=0 <1.11.1

## Details
The package libvcs before 0.11.1 are vulnerable to Command Injection via argument injection. When calling the update_repo function (when using hg), the url parameter is passed to the hg clone command. By injecting some hg options it was possible to get arbitrary command execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21187
- https://github.com/vcs-python/libvcs/pull/306
- https://github.com/vcs-python/vcspull/commit/e1b77128a1fa0754625b5f43d8bc47956f21f33e
- https://github.com/pypa/advisory-database/tree/main/vulns/libvcs/PYSEC-2022-163.yaml
- https://github.com/vcs-python/libvcs/blob/master/CHANGES#libvcs-0111-2022-03-12
- https://github.com/vcs-python/libvcs/blob/v0.11.1/CHANGES%23libvcs-0111-2022-03-12
- https://github.com/vcs-python/vcspull/blob/master/CHANGES#vcspull-1111-2022-03-12
- https://snyk.io/vuln/SNYK-PYTHON-LIBVCS-2421204
