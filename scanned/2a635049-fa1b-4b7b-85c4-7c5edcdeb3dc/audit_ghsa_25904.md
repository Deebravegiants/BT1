# [H] Missing Authentication for Critical Function in Foreman Ansible

## Summary
Severity: High
Advisory: GHSA-vvff-6wrr-4g7q
CVE: CVE-2021-3589
CWE: CWE-306
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-24
Source: https://github.com/advisories/GHSA-vvff-6wrr-4g7q
Type: github-advisory

## Affected
- RubyGems: `foreman_ansible` — affected >=0 <2.0.0

## Details
An authorization flaw was found in Foreman Ansible. An authenticated attacker with certain permissions to create and run Ansible jobs can access hosts through job templates. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3589
- https://github.com/theforeman/foreman_ansible/commit/a5e0827bc3ec6c8ab82f968907857a15646305d5
- https://access.redhat.com/security/cve/CVE-2021-3589
- https://bugzilla.redhat.com/show_bug.cgi?id=1969265
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/foreman_ansible/CVE-2021-3589.yml
- https://github.com/theforeman/foreman_ansible
