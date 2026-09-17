# [H] Ansible exposes sensitive data in log files and on the terminal

## Summary
Severity: High
Advisory: GHSA-jwcc-j78w-j73w
CVE: CVE-2018-10855
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-jwcc-j78w-j73w
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.5.0a1 <2.5.5
- PyPI: `ansible` — affected >=2.4.0.0 <2.4.5.0

## Details
Ansible 2.5 prior to 2.5.5, and 2.4 prior to 2.4.5, do not honor the no_log task flag for failed tasks. When the no_log flag has been used to protect sensitive data passed to a task from being logged, and that task does not run successfully, Ansible will expose sensitive data in log files and on the terminal of the user running Ansible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10855
- https://access.redhat.com/errata/RHBA-2018:3788
- https://access.redhat.com/errata/RHSA-2018:1948
- https://access.redhat.com/errata/RHSA-2018:1949
- https://access.redhat.com/errata/RHSA-2018:2022
- https://access.redhat.com/errata/RHSA-2018:2079
- https://access.redhat.com/errata/RHSA-2018:2184
- https://access.redhat.com/errata/RHSA-2018:2585
- https://access.redhat.com/errata/RHSA-2019:0054
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10855
- https://github.com/advisories/GHSA-jwcc-j78w-j73w
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-42.yaml
- https://usn.ubuntu.com/4072-1
- https://www.debian.org/security/2019/dsa-4396
