# [H] OpenStack keystonemiddleware and python-keystoneclient vulnerable to man-in-the-middle attacks

## Summary
Severity: High
Advisory: GHSA-p9wq-mjh8-q72m
CVE: CVE-2015-1852
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p9wq-mjh8-q72m
Type: github-advisory

## Affected
- PyPI: `keystonemiddleware` — affected >=0 <1.6.0
- PyPI: `python-keystoneclient` — affected >=0 <1.4.0

## Details
The s3_token middleware in OpenStack keystonemiddleware before 1.6.0 and python-keystoneclient before 1.4.0 disables certification verification when the "insecure" option is set in a paste configuration (paste.ini) file regardless of the value, which allows remote attackers to conduct man-in-the-middle attacks via a crafted certificate, a different vulnerability than CVE-2014-7144.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1852
- https://access.redhat.com/errata/RHSA-2015:1677
- https://access.redhat.com/errata/RHSA-2015:1685
- https://access.redhat.com/security/cve/CVE-2015-1852
- https://bugs.launchpad.net/keystonemiddleware/+bug/1411063
- https://bugzilla.redhat.com/show_bug.cgi?id=1209527
- https://github.com/pypa/advisory-database/tree/main/vulns/keystonemiddleware/PYSEC-2015-30.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/python-keystoneclient/PYSEC-2015-31.yaml
- https://web.archive.org/web/20200228060649/http://www.securityfocus.com/bid/74187
- http://lists.openstack.org/pipermail/openstack-announce/2015-April/000350.html
- http://rhn.redhat.com/errata/RHSA-2015-1677.html
- http://rhn.redhat.com/errata/RHSA-2015-1685.html
- http://www.oracle.com/technetwork/topics/security/bulletinapr2015-2511959.html
- http://www.ubuntu.com/usn/USN-2705-1
