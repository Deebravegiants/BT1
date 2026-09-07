# [C] Python Swift client is vulnerable to Missing SSL Certificate Check

## Summary
Severity: Critical
Advisory: GHSA-p3xv-97g8-4wmj
CVE: CVE-2013-6396
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p3xv-97g8-4wmj
Type: github-advisory

## Affected
- PyPI: `python-swiftclient` — affected >=1.0 <2.0

## Details
The OpenStack Python client library for Swift (python-swiftclient) from 1.0 before 2.0 does not verify X.509 certificates from SSL servers, which allows man-in-the-middle attackers to spoof servers and obtain sensitive information via a crafted certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6396
- https://github.com/openstack/python-swiftclient/commit/b182112719ab87942472e44aa3446ea0eb19a289
- https://bugs.launchpad.net/python-swiftclient/+bug/1199783
- https://github.com/chmouel/python-swiftclient
- https://github.com/pypa/advisory-database/tree/main/vulns/python-swiftclient/PYSEC-2014-12.yaml
- https://review.opendev.org/c/openstack/python-swiftclient/+/69187
- http://www.openwall.com/lists/oss-security/2014/02/17/7
