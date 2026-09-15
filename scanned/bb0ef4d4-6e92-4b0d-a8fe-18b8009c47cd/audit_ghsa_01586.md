# [M] Arbitrary Code Execution in blazar-dashboard

## Summary
Severity: Medium
Advisory: GHSA-939m-4xpw-v34v
CVE: CVE-2020-26943
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-939m-4xpw-v34v
Type: github-advisory

## Affected
- PyPI: `blazar-dashboard` — affected >=0 <1.3.1
- PyPI: `blazar-dashboard` — affected >=2.0.0 <2.0.1
- PyPI: `blazar-dashboard` — affected >=3.0.0 <3.0.1

## Details
An issue was discovered in OpenStack blazar-dashboard before 1.3.1, 2.0.0, and 3.0.0. A user allowed to access the Blazar dashboard in Horizon may trigger code execution on the Horizon host as the user the Horizon service runs under (because the Python eval function is used). This may result in Horizon host unauthorized access and further compromise of the Horizon service. All setups using the Horizon dashboard with the blazar-dashboard plugin are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26943
- https://github.com/pypa/advisory-database/tree/main/vulns/blazar-dashboard/PYSEC-2020-225.yaml
- https://launchpad.net/bugs/1895688
- https://review.opendev.org/755810
- https://review.opendev.org/755812
- https://review.opendev.org/755813
- https://review.opendev.org/755814
- https://review.opendev.org/756064
- https://security.openstack.org/ossa/OSSA-2020-007.html
- http://www.openwall.com/lists/oss-security/2020/10/16/5
