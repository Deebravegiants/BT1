# [H] python-glanceclient vulnerable to SSL server spoofing due to unverified X.509 certificate

## Summary
Severity: High
Advisory: GHSA-qgfg-gvff-523v
CVE: CVE-2013-4111
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qgfg-gvff-523v
Type: github-advisory

## Affected
- PyPI: `python-glanceclient` — affected >=0 <0.10.0

## Details
The Python client library for Glance (python-glanceclient) before 0.10.0 does not properly check the preverify_ok value, which prevents the server hostname from being verified with a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate and allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4111
- https://access.redhat.com/errata/RHSA-2013:1200
- https://access.redhat.com/security/cve/CVE-2013-4111
- https://bugs.launchpad.net/ossa/+bug/1192229
- https://bugzilla.redhat.com/show_bug.cgi?id=989738
- https://github.com/jaypipes/python-glanceclient
- https://github.com/openstack/python-glanceclient/blob/master/doc/source/index.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/python-glanceclient/PYSEC-2013-11.yaml
- http://lists.opensuse.org/opensuse-updates/2013-08/msg00019.html
- http://rhn.redhat.com/errata/RHSA-2013-1200.html
- http://www.ubuntu.com/usn/USN-2004-1
