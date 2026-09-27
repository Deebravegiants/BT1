# [H] Ansible does not verify that the server hostname matches a domain name in certificates

## Summary
Severity: High
Advisory: GHSA-w64c-pxjj-h866
CVE: CVE-2015-3908
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-w64c-pxjj-h866
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.9.2

## Details
Ansible before 1.9.2 does not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3908
- https://github.com/advisories/GHSA-w64c-pxjj-h866
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2015-1.yaml
- https://lists.debian.org/debian-lts-announce/2019/09/msg00016.html
- http://lists.opensuse.org/opensuse-updates/2015-07/msg00051.html
- http://lists.opensuse.org/opensuse-updates/2015-08/msg00029.html
- http://www.ansible.com/security
- http://www.openwall.com/lists/oss-security/2015/07/14/4
