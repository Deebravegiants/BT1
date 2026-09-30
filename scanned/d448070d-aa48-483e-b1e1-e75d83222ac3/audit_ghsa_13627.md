# [M] Ansible may expose private key

## Summary
Severity: Medium
Advisory: GHSA-ww3m-ffrm-qvqv
CVE: CVE-2023-4237
CWE: CWE-497
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-04
Source: https://github.com/advisories/GHSA-ww3m-ffrm-qvqv
Type: github-advisory

## Affected
- PyPI: `ansible-core` — affected >=2.8.0

## Details
A flaw was found in the Ansible Automation Platform. When creating a new keypair, the ec2_key module prints out the private key directly to the standard output. This flaw allows an attacker to fetch those keys from the log files, compromising the system's confidentiality, integrity, and availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4237
- https://access.redhat.com/errata/RHBA-2023:5653
- https://access.redhat.com/errata/RHBA-2023:5666
- https://access.redhat.com/security/cve/CVE-2023-4237
- https://bugzilla.redhat.com/show_bug.cgi?id=2229979
- https://github.com/ansible/ansible
