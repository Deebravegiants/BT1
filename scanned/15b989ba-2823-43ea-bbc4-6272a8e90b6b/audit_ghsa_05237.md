# [M] OpenStack Ironic can return unredacted sensitive information when applying a PATCH to update fields in volume properties

## Summary
Severity: Medium
Advisory: GHSA-j4cw-mcg2-2q78
CVE: CVE-2026-54421
CWE: CWE-212
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-14
Source: https://github.com/advisories/GHSA-j4cw-mcg2-2q78
Type: github-advisory

## Affected
- PyPI: `ironic` — affected >=17.0.0 <29.0.6
- PyPI: `ironic` — affected >=30.0.0 <32.0.2
- PyPI: `ironic` — affected >=33.0.0 <35.0.2
- PyPI: `ironic` — affected >=36.0.0 <37.0.1

## Details
In OpenStack Ironic through 35.0.1, when applying a PATCH to update fields in volume properties the user is authorized for, Ironic can return unredacted sensitive information (such as iSCSI credentials). The PATCH outcome is a security issue; the POST outcome is not a security issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-54421
- https://github.com/openstack/ironic/commit/dd2df520fe0ae019cb247a8295542abc2d4b46dd
- https://bugs.launchpad.net/ironic/+bug/2155049
- https://github.com/openstack/ironic
- https://review.opendev.org/c/openstack/ironic/+/990430
- https://security.openstack.org/ossa/OSSA-2026-023.html
- http://www.openwall.com/lists/oss-security/2026/06/16/10
