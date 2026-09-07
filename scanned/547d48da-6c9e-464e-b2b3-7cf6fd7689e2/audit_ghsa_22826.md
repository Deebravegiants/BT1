# [M] Ceilometer Prints Sensitive Configuration Data to Log

## Summary
Severity: Medium
Advisory: GHSA-2cvf-r9jm-4qm9
CVE: CVE-2019-3830
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2cvf-r9jm-4qm9
Type: github-advisory

## Affected
- PyPI: `ceilometer` — affected >=0 <12.0.0.0rc1

## Details
A vulnerability was found in ceilometer before version 12.0.0.0rc1. An Information Exposure in ceilometer-agent prints sensitive configuration data to log files without DEBUG logging being activated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3830
- https://github.com/openstack/ceilometer/commit/8881a42af169a2d7c912b1434911f978883c83f3
- https://github.com/openstack/ceilometer/commit/8881a42af169a2d7c912b1434911f978883c83f3#diff-f2d2273521cce7e69f7032c6185936736a5acc70b2b2f90d956b9a7998b087cd
- https://access.redhat.com/errata/RHSA-2019:0919
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3830
- https://github.com/openstack/ceilometer
- https://github.com/pypa/advisory-database/tree/main/vulns/ceilometer/PYSEC-2019-78.yaml
