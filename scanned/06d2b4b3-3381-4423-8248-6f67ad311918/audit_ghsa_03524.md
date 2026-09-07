# [M] Execution of untrusted code through config file

## Summary
Severity: Medium
Advisory: GHSA-8278-88vv-x98r
CVE: CVE-2021-21371
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-10
Source: https://github.com/advisories/GHSA-8278-88vv-x98r
Type: github-advisory

## Affected
- PyPI: `tenable-jira-cloud` — affected >=0 <1.1.21

## Details
### Impact
It is possible to run arbitrary commands through the yaml.load() method.  This could allow an attacker with local access to the host to run arbitrary code by running the application with a specially crafted YAML configuration file.

### Workarounds
Manually adjust yaml.load() to yaml.safe_load()

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [tenable/integration-jira-cloud](https://github.com/tenable/integration-jira-cloud/issues)
* Email us at [vulnreport@tenable.com](mailto:vulnreport@tenable.com)

## References
- https://github.com/tenable/integration-jira-cloud/security/advisories/GHSA-8278-88vv-x98r
- https://nvd.nist.gov/vuln/detail/CVE-2021-21371
- https://github.com/tenable/integration-jira-cloud/commit/f8c2095fd529e664e7fa25403a0a4a85bb3907d0
- https://github.com/pypa/advisory-database/tree/main/vulns/tenable-jira-cloud/PYSEC-2021-60.yaml
- https://github.com/tenable/integration-jira-cloud
- https://pypi.org/project/tenable-jira-cloud
