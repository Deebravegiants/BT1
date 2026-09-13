# [M] OpenStack Compute (Nova) Improper Input Validation

## Summary
Severity: Medium
Advisory: GHSA-46r8-9cj7-pw6g
CVE: CVE-2012-2654
CWE: CWE-20
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-46r8-9cj7-pw6g
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
The (1) EC2 and (2) OS APIs in OpenStack Compute (Nova) Folsom (2012.2), Essex (2012.1), and Diablo (2011.3) do not properly check the protocol when security groups are created and the network protocol is not specified entirely in lowercase, which allows remote attackers to bypass intended access restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2654
- https://github.com/openstack/nova/commit/9f9e9da777161426a6f8cb4314b78e09beac2978
- https://github.com/openstack/nova/commit/ff06c7c885dc94ed7c828e8cdbb8b5d850a7e654
- https://bugs.launchpad.net/nova/+bug/985184
- https://exchange.xforce.ibmcloud.com/vulnerabilities/76110
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2012-37.yaml
- https://lists.launchpad.net/openstack/msg12883.html
- https://review.openstack.org/#/c/8239
- http://www.ubuntu.com/usn/USN-1466-1
