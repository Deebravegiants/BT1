# [H] oslo.middleware Information Disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-xcp8-hh74-f6mc
CVE: CVE-2017-2592
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-xcp8-hh74-f6mc
Type: github-advisory

## Affected
- PyPI: `oslo.middleware` — affected >=3.9.0 <3.19.1
- PyPI: `oslo.middleware` — affected >=0 <3.8.1
- PyPI: `oslo.middleware` — affected >=3.20.0 <3.23.1
- PyPI: `oslo-middleware` — affected >=3.9.0 <3.19.1
- PyPI: `oslo-middleware` — affected >=0 <3.8.1
- PyPI: `oslo-middleware` — affected >=3.20.0 <3.23.1

## Details
python-oslo-middleware before versions 3.8.1, 3.19.1, 3.23.1 is vulnerable to an information disclosure. Software using the CatchError class could include sensitive values in a traceback's error message. System users could exploit this flaw to obtain sensitive information from OpenStack component error logs (for example, keystone tokens).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2592
- https://access.redhat.com/errata/RHSA-2017:0300
- https://access.redhat.com/errata/RHSA-2017:0435
- https://bugs.launchpad.net/keystonemiddleware/+bug/1628031
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2592
- https://github.com/advisories/GHSA-xcp8-hh74-f6mc
- https://github.com/openstack/oslo.middleware
- https://github.com/pypa/advisory-database/tree/main/vulns/oslo-middleware/PYSEC-2018-104.yaml
- https://review.openstack.org/#/c/425730
- https://review.openstack.org/#/c/425732
- https://review.openstack.org/#/c/425734
- https://usn.ubuntu.com/3666-1
- http://lists.openstack.org/pipermail/openstack-announce/2017-January/002002.html
- http://rhn.redhat.com/errata/RHSA-2017-0300.html
- http://rhn.redhat.com/errata/RHSA-2017-0435.html
