# [M] Ansible Logs Passwords If PowerShell ScriptBlock is Enabled

## Summary
Severity: Medium
Advisory: GHSA-v735-2pp6-h86r
CVE: CVE-2018-16859
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v735-2pp6-h86r
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.3
- PyPI: `ansible` — affected >=0 <2.5.12
- PyPI: `ansible` — affected >=2.6.0a1 <2.6.9

## Details
Execution of Ansible playbooks on Windows platforms with PowerShell ScriptBlock logging and Module logging enabled can allow for 'become' passwords to appear in EventLogs in plaintext. A local user with administrator privileges on the machine can view these logs and discover the plaintext password. Ansible Engine 2.8 and older are believed to be vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16859
- https://github.com/ansible/ansible/pull/49142
- https://github.com/ansible/ansible/commit/0d746b4198abf84290a093b83cf02b4203d73d9f
- https://github.com/ansible/ansible/commit/2f8d3fcf41107efafc14d51ab6e14531ca8f8c87
- https://github.com/ansible/ansible/commit/4d748d34f9392aa469da00a85c8e2d5fe6cec52b
- https://access.redhat.com/errata/RHSA-2018:3770
- https://access.redhat.com/errata/RHSA-2018:3771
- https://access.redhat.com/errata/RHSA-2018:3772
- https://access.redhat.com/errata/RHSA-2018:3773
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16859
- https://github.com/ansible/ansible
- https://github.com/ansible/ansible/blob/v2.5.13/changelogs/CHANGELOG-v2.5.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-60.yaml
- https://web.archive.org/web/20200227102121/http://www.securityfocus.com/bid/106004
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00077.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00020.html
