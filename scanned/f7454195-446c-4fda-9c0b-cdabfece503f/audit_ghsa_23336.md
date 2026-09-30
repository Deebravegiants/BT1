# [M] OpenStack Glance sensitive information disclosure via logs

## Summary
Severity: Medium
Advisory: GHSA-4xw6-hj5p-4j79
CVE: CVE-2014-1948
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4xw6-hj5p-4j79
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=0 <11.0.0a0

## Details
OpenStack Image Registry and Delivery Service (Glance) 2013.2 through 2013.2.1 and Icehouse before icehouse-2 logs a URL containing the Swift store backend password when authentication fails and WARNING level logging is enabled, which allows local users to obtain sensitive information by reading the log.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1948
- https://github.com/openstack/glance/commit/108f0e04ad2ed3dc287f1b71b987a7e9d66072ba
- https://github.com/openstack/glance/commit/f6e41e9c0ff3aa9ee57b8c8ed8c789f1aff019bc
- https://bugs.launchpad.net/glance/+bug/1275062
- https://github.com/openstack/glance
- https://github.com/pypa/advisory-database/tree/main/vulns/glance/PYSEC-2014-102.yaml
- http://rhn.redhat.com/errata/RHSA-2014-0229.html
- http://www.openwall.com/lists/oss-security/2014/02/12/18
