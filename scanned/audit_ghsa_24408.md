# [M] OpenStack Nova Multiple directory traversal vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-qr62-r9xc-r2gj
CVE: CVE-2011-4596
CWE: CWE-22
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qr62-r9xc-r2gj
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
Multiple directory traversal vulnerabilities in OpenStack Nova before 2011.3.1, when the EC2 API and the S3/RegisterImage image-registration method are enabled, allow remote authenticated users to overwrite arbitrary files via a crafted (1) tarball or (2) manifest.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4596
- https://github.com/openstack/nova/commit/76363226bd8533256f7795bba358d7f4b8a6c9e6
- https://github.com/openstack/nova/commit/ad3241929ea00569c74505ed002208ce360c667e
- https://bugs.launchpad.net/nova/+bug/885167
- https://bugs.launchpad.net/nova/+bug/894755
- https://github.com/openstack/nova
- https://lists.launchpad.net/openstack/msg06105.html
