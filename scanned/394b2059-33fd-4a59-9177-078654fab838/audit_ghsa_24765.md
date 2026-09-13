# [H] Ansible sensitive information disclosure

## Summary
Severity: High
Advisory: GHSA-j569-fghw-f9rx
CVE: CVE-2018-16876
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j569-fghw-f9rx
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.5.14
- PyPI: `ansible` — affected >=2.6.0a1 <2.6.11
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.5

## Details
ansible before versions 2.5.14, 2.6.11, 2.7.5 is vulnerable to a information disclosure flaw in `vvv+` mode with no_log on that can lead to leakage of sensible data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16876
- https://github.com/ansible/ansible/issues/51318
- https://github.com/ansible/ansible/pull/49569
- https://github.com/ansible/ansible/commit/e0a81d133ffc8f7067182c53cf6a28c724dd1099
- https://github.com/ansible/ansible/commit/0954942dfdc563f80fd3e388f550aa165ec931da
- https://github.com/ansible/ansible/commit/424c68f15ad9f532d73e5afed33ff477f54281a7
- https://www.debian.org/security/2019/dsa-4396
- https://web.archive.org/web/20200227100904/http://www.securityfocus.com/bid/106225
- https://usn.ubuntu.com/4072-1
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2019-141.yaml
- https://github.com/ansible/ansible
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16876
- https://access.redhat.com/errata/RHSA-2019:0590
- https://access.redhat.com/errata/RHSA-2019:0564
- https://access.redhat.com/errata/RHSA-2018:3838
- https://access.redhat.com/errata/RHSA-2018:3837
- https://access.redhat.com/errata/RHSA-2018:3836
- https://access.redhat.com/errata/RHSA-2018:3835
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00077.html
