# [M] Ansible leaks sensitive information to logs when told not to

## Summary
Severity: Medium
Advisory: GHSA-h653-95qw-h2mp
CVE: CVE-2019-14858
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h653-95qw-h2mp
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.0rc4
- PyPI: `ansible` — affected >=2.8.0a1 <2.8.6
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.14
- PyPI: `ansible` — affected >=2.0 <2.6.20

## Details
A vulnerability was found in Ansible engine 2.x up to 2.8 and Ansible tower 3.x up to 3.5. When a module has an argument_spec with sub parameters marked as `no_log`, passing an invalid parameter name to the module will cause the task to fail before the `no_log` options in the sub parameters are processed. As a result, data in the sub parameter fields will not be masked and will be displayed if Ansible is run with increased verbosity and present in the module invocation arguments for the task.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14858
- https://github.com/ansible/ansible/pull/63405
- https://github.com/ansible/ansible/commit/0fd656e9964a91f2e8b1e9bbf78c74661ab9d37b
- https://github.com/ansible/ansible/commit/3dfb8e81bb5f776a6b00c7a90dd087e85b71f8bb
- https://github.com/ansible/ansible/commit/87f8d77d70476454f7fe2381bd363a329ce4266c
- https://github.com/ansible/ansible/commit/f610ed3a4eb87eb557200606279796921fa9b722
- https://access.redhat.com/errata/RHSA-2019:3201
- https://access.redhat.com/errata/RHSA-2019:3202
- https://access.redhat.com/errata/RHSA-2019:3203
- https://access.redhat.com/errata/RHSA-2019:3207
- https://access.redhat.com/errata/RHSA-2020:0756
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14858
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2019-171.yaml
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00026.html
