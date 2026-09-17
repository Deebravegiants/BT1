# [H] ansible-core: Argument injection in ansible-galaxy role install leads to arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-w8p5-mx5w-cpqj
CVE: CVE-2026-11332
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-w8p5-mx5w-cpqj
Type: github-advisory

## Affected
- PyPI: `ansible-core` — affected >=0 <2.16.19rc1
- PyPI: `ansible-core` — affected >=2.17.0b1 <2.18.18rc1
- PyPI: `ansible-core` — affected >=2.19.0b1 <2.19.11rc1
- PyPI: `ansible-core` — affected >=2.20.0b1 <2.20.7rc1
- PyPI: `ansible-core` — affected >=2.21.0b1 <2.21.1rc1

## Details
A flaw was found in ansible-core. The ansible-galaxy role install command processes dependency specifications from a role's meta/requirements.yml file. Due to improper neutralization of argument delimiters, a malicious role author can inject arbitrary git configuration flags through the src field. This allows arbitrary code execution on the machine of a user who installs the role via ansible-galaxy role install.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11332
- https://github.com/ansible/ansible/pull/87070
- https://github.com/ansible/ansible/commit/edee59aa15abcc74d920bb3e9c3835ab8db05a2f
- https://access.redhat.com/security/cve/CVE-2026-11332
- https://bugzilla.redhat.com/show_bug.cgi?id=2485379
- https://github.com/ansible/ansible
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-11332.json
