# [M] Ansible Arbitrary File Overwrite Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pcqv-c46v-2p4v
CVE: CVE-2013-4260
CWE: CWE-281
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pcqv-c46v-2p4v
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=1.2 <1.2.3

## Details
`lib/ansible/playbook/__init__.py` in Ansible 1.2.x before 1.2.3, when playbook does not run due to an error, allows local users to overwrite arbitrary files via a symlink attack on a retry file with a predictable name in `/var/tmp/ansible/`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4260
- https://github.com/ansible/ansible/commit/d5948d59fc863fcec6efa62fa2791928ffc5a6d1
- https://bugzilla.redhat.com/show_bug.cgi?id=998227
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86898
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2013-2.yaml
- https://groups.google.com/forum/#!topic/ansible-project/UVDYW0HGcNg
- https://groups.google.com/forum/#%21topic/ansible-project/UVDYW0HGcNg
- http://www.ansible.com/security
