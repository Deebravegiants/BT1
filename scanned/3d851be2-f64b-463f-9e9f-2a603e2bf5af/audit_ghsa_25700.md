# [M] OpenStack Nova Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-vcmv-6rxx-fh7r
CVE: CVE-2011-4076
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-vcmv-6rxx-fh7r
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
OpenStack Nova before 2012.1 allows someone with access to an EC2_ACCESS_KEY (equivalent to a username) to obtain the EC2_SECRET_KEY (equivalent to a password). Exposing the EC2_ACCESS_KEY via http or tools that allow man-in-the-middle over https could allow an attacker to easily obtain the EC2_SECRET_KEY. An attacker could also presumably brute force values for EC2_ACCESS_KEY.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4076
- https://github.com/openstack/nova/commit/b1ab6da1495784ff581000018a6047fd19cf82c4
- https://github.com/openstack/nova/commit/beee11edbfdd82cd81bc9c0fd75912c167892c2b
- https://access.redhat.com/security/cve/cve-2011-4076
- https://bugs.launchpad.net/nova/+bug/868360
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-4076
- https://security-tracker.debian.org/tracker/CVE-2011-4076
- https://www.openwall.com/lists/oss-security/2011/10/25/4
