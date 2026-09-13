# [H] OpenStack Compute (Nova) Denial of service via a large number of calls to the addFixedIp function

## Summary
Severity: High
Advisory: GHSA-63fq-8fp9-vhwq
CVE: CVE-2013-1838
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-63fq-8fp9-vhwq
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
OpenStack Compute (Nova) Grizzly, Folsom (2012.2), and Essex (2012.1) does not properly implement a quota for fixed IPs, which allows remote authenticated users to cause a denial of service (resource exhaustion and failure to spawn new instances) via a large number of calls to the addFixedIp function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1838
- https://github.com/openstack/nova/commit/9561484166f245d0e4602a36351d6cac72dd9426
- https://github.com/openstack/nova/commit/99429214d4ddb5bdc7de185693b8a53ad50df3c6
- https://github.com/openstack/nova/commit/efaacdaee116388234558e2682b647d41fe5b149
- https://bugs.launchpad.net/nova/+bug/1125468
- https://bugzilla.redhat.com/show_bug.cgi?id=919648
- https://exchange.xforce.ibmcloud.com/vulnerabilities/82877
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2013-44.yaml
- https://lists.launchpad.net/openstack/msg21892.html
- https://review.openstack.org/#/c/24451
- https://review.openstack.org/#/c/24452
- https://review.openstack.org/#/c/24453
- http://rhn.redhat.com/errata/RHSA-2013-0709.html
- http://ubuntu.com/usn/usn-1771-1
- http://www.openwall.com/lists/oss-security/2013/03/14/18
