# [M] OpenStack Nova Long server names grow nova-api log files significantly

## Summary
Severity: Medium
Advisory: GHSA-pjvw-p2v5-wf6q
CVE: CVE-2012-1585
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pjvw-p2v5-wf6q
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
OpenStack Compute (Nova) Essex before 2011.3 allows remote authenticated users to cause a denial of service (Nova-API log file and disk consumption) via a long server name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1585
- https://bugs.launchpad.net/nova/+bug/962515
- https://github.com/openstack/nova
- http://github.com/openstack/nova/commit/0fa7d12dbfb7ae016657dd91034b4c0781ea43de
- http://github.com/openstack/nova/commit/1ebec5726c7a9db0a6f29fad0ef747b0c087f702
- http://github.com/openstack/nova/commit/c7f526fae6062e9ab51f65474af71d496aa66554
- http://github.com/openstack/nova/commit/c869a41951b77c6930bf4fb4734f05cd3d6ac4b1
- http://lwn.net/Alerts/491298
- http://osdir.com/ml/openstack-cloud-computing/2012-03/msg01133.html
