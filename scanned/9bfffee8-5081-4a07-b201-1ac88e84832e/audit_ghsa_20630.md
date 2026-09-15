# [H] ansible-runner vulnerable to shell command injection

## Summary
Severity: High
Advisory: GHSA-6j58-grhv-2769
CVE: CVE-2021-4041
CWE: CWE-116, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-25
Source: https://github.com/advisories/GHSA-6j58-grhv-2769
Type: github-advisory

## Affected
- PyPI: `ansible-runner` — affected >=0 <2.1.0

## Details
A flaw was found in ansible-runner. An improper escaping of the shell command, while calling the `ansible_runner.interface.run_command`, can lead to parameters getting executed as host's shell command. A developer could unintentionally write code that gets executed in the host rather than the virtual environment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4041
- https://github.com/ansible/ansible-runner/commit/3533f265f4349a3f2a0283158cd01b59a6bbc7bd
- https://access.redhat.com/security/cve/CVE-2021-4041
- https://bugzilla.redhat.com/show_bug.cgi?id=2028074
- https://github.com/advisories/GHSA-6j58-grhv-2769
- https://github.com/ansible/ansible-runner
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible-runner/PYSEC-2022-253.yaml
