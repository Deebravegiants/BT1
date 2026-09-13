# [M] OpenStack Nova Denial of Service in network source security groups

## Summary
Severity: Medium
Advisory: GHSA-ph2h-hh49-vh27
CVE: CVE-2013-4185
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-ph2h-hh49-vh27
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
Algorithmic complexity vulnerability in OpenStack Compute (Nova) before 2013.1.3 and Havana before havana-3 does not properly handle network source security group policy updates, which allows remote authenticated users to cause a denial of service (nova-network consumption) via a large number of server-creation operations, which triggers a large number of update requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4185
- https://bugs.launchpad.net/nova/+bug/1184041
- https://github.com/openstack/nova
- http://github.com/openstack/nova/commit/52ad911963da4095b213952dee3a430fe0c4c30f
- http://github.com/openstack/nova/commit/85aac04704350566d6b06aa7a3b99649946c672c
- http://github.com/openstack/nova/commit/d4ee081c5c0a5132781235177c430ebcf72b0b0b
- http://rhn.redhat.com/errata/RHSA-2013-1199.html
- http://seclists.org/oss-sec/2013/q3/282
