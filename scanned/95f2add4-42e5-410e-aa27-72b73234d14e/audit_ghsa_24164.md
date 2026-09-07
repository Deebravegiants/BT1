# [H] OpenStack Nova VMWare driver leaks rescued images

## Summary
Severity: High
Advisory: GHSA-jv34-xvjq-ppch
CVE: CVE-2014-2573
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jv34-xvjq-ppch
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
The VMWare driver in OpenStack Compute (Nova) 2013.2 through 2013.2.2 does not properly put VMs into RESCUE status, which allows remote authenticated users to bypass the quota limit and cause a denial of service (resource consumption) by requesting the VM be put into rescue and then deleting the image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2573
- https://github.com/openstack/nova/commit/b3cc3f62a60662e5bb82136c0cfa464592a6afe9
- https://github.com/openstack/nova/commit/efb66531bc37ee416778a70d46c657608ca767af
- https://bugs.launchpad.net/nova/+bug/1269418
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2014-113.yaml
- http://www.openwall.com/lists/oss-security/2014/03/21/1
- http://www.openwall.com/lists/oss-security/2014/03/21/2
