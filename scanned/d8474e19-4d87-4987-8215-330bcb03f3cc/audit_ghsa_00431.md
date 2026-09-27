# [C] Ansible fails to cache SSH host keys

## Summary
Severity: Critical
Advisory: GHSA-9x6q-5423-w5v9
CVE: CVE-2013-2233
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-9x6q-5423-w5v9
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.2.1

## Details
Ansible before 1.2.1 makes it easier for remote attackers to conduct man-in-the-middle attacks by leveraging failure to cache SSH host keys.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2233
- https://github.com/ansible/ansible/issues/857
- https://bugzilla.redhat.com/show_bug.cgi?id=980821
- https://github.com/advisories/GHSA-9x6q-5423-w5v9
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-36.yaml
- https://www.ansible.com/security
- http://www.openwall.com/lists/oss-security/2013/07/01/2
- http://www.openwall.com/lists/oss-security/2013/07/02/6
