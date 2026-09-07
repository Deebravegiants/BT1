# [H] Ansible Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-3xvg-x47j-x75w
CVE: CVE-2018-10874
CWE: CWE-20, CWE-426
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3xvg-x47j-x75w
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.4.6.0
- PyPI: `ansible` — affected >=2.5 <2.5.6
- PyPI: `ansible` — affected >=2.6 <2.6.1

## Details
In ansible it was found that inventory variables are loaded from current working directory when running ad-hoc command which are under attacker's control, allowing to run arbitrary code as a result.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10874
- https://github.com/ansible/ansible/pull/42067
- https://github.com/ansible/ansible/commit/44874addc7ea136f83c67d5869047ece02645fdb
- https://github.com/ansible/ansible/commit/1f80949f964a946773f9d3ac1899535bd2cc2b8e
- https://github.com/ansible/ansible/commit/10d6fe6c98cfee9a7be0fea6102ba5dec951aec7
- https://web.archive.org/web/20201130165946/http://www.securitytracker.com/id/1041396
- https://usn.ubuntu.com/4072-1
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-81.yaml
- https://github.com/ansible/ansible
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10874
- https://bugzilla.redhat.com/show_bug.cgi?id=1596528
- https://access.redhat.com/security/cve/CVE-2018-10874
- https://access.redhat.com/errata/RHSA-2019:0054
- https://access.redhat.com/errata/RHSA-2018:2585
- https://access.redhat.com/errata/RHSA-2018:2321
- https://access.redhat.com/errata/RHSA-2018:2166
- https://access.redhat.com/errata/RHSA-2018:2152
- https://access.redhat.com/errata/RHSA-2018:2151
- https://access.redhat.com/errata/RHSA-2018:2150
- https://access.redhat.com/errata/RHBA-2018:3788
