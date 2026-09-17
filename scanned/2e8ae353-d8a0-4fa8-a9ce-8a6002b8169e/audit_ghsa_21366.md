# [M] Plaintext storage of tokens in pulp_ansible

## Summary
Severity: Medium
Advisory: GHSA-qv37-mfjf-42h8
CVE: CVE-2022-3644
CWE: CWE-256, CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-qv37-mfjf-42h8
Type: github-advisory

## Affected
- PyPI: `pulp-ansible` — affected >=0 <0.15.0

## Details
The collection remote for pulp_ansible stores tokens in plaintext instead of using pulp's encrypted field and exposes them in read/write mode via the API () instead of marking it as write only.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3644
- https://github.com/pulp/pulp_ansible/issues/1221
- https://github.com/pulp/pulp_ansible/commit/d13c427b09482a7f598d8ee597d17a8a34888665
- https://github.com/pulp/pulp_ansible
- https://github.com/pulp/pulp_ansible/blob/main/pulp_ansible/app/models.py#L234
