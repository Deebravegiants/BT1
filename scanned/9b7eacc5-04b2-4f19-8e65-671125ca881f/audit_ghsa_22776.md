# [H] OpenStack keystonemiddleware does not verify certificate

## Summary
Severity: High
Advisory: GHSA-7f2c-vp52-gmfw
CVE: CVE-2014-7144
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7f2c-vp52-gmfw
Type: github-advisory

## Affected
- PyPI: `keystonemiddleware` — affected >=0 <0.11.0
- PyPI: `keystonemiddleware` — affected >=1.0 <1.2.0
- PyPI: `python-keystoneclient` — affected >=0 <0.11.0
- PyPI: `python-keystoneclient` — affected >=1.0 <1.2.0

## Details
OpenStack keystonemiddleware (formerly python-keystoneclient) 0.x before 0.11.0 and 1.x before 1.2.0 disables certification verification when the "insecure" option is set in a paste configuration (`paste.ini`) file regardless of the value, which allows remote attackers to conduct man-in-the-middle attacks via a crafted certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7144
- https://bugs.launchpad.net/python-keystoneclient/+bug/1353315
- https://github.com/openstack/ossa/blob/23e15de721f4a6890374a231d93524e02965a97f/ossa/OSSA-2014-030.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/keystonemiddleware/PYSEC-2014-26.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/python-keystoneclient/PYSEC-2014-71.yaml
- https://web.archive.org/web/20200228053850/http://www.securityfocus.com/bid/69864
- https://web.archive.org/web/20200228060511/https://www.securityfocus.com/bid/69864
- http://rhn.redhat.com/errata/RHSA-2014-1783.html
- http://rhn.redhat.com/errata/RHSA-2014-1784.html
- http://rhn.redhat.com/errata/RHSA-2015-0020.html
- http://www.openwall.com/lists/oss-security/2014/09/25/51
- http://www.ubuntu.com/usn/USN-2705-1
