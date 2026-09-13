# [M] Ansible does not collect garbage after playbook run

## Summary
Severity: Medium
Advisory: GHSA-f556-49jc-4rvc
CVE: CVE-2020-25635
CWE: CWE-212
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-31
Source: https://github.com/advisories/GHSA-f556-49jc-4rvc
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.10.1

## Details
A flaw was found in Ansible Base when using the aws_ssm connection plugin as its garbage collector is not happening after the playbook run is completed. Files would remain in the bucket exposing the data. This issue directly affects data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25635
- https://github.com/ansible-collections/community.aws/issues/222
- https://github.com/ansible-collections/community.aws/pull/237#issuecomment-1468591094
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-25635
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-220.yaml
