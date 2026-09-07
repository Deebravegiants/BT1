# [M] Ansible template injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7j69-qfc3-2fq9
CVE: CVE-2023-5764
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-7j69-qfc3-2fq9
Type: github-advisory

## Affected
- PyPI: `ansible-core` — affected >=2.16.0 <2.16.1
- PyPI: `ansible-core` — affected >=2.15.0 <2.15.8
- PyPI: `ansible-core` — affected >=0 <2.14.12

## Details
A template injection flaw was found in Ansible where a user's controller internal templating operations may remove the unsafe designation from template data. This issue could allow an attacker to use a specially crafted file to introduce templating injection when supplying templating data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5764
- https://github.com/ansible/ansible/commit/270b39f6ff02511a2199505161218cbd1a5ae34f
- https://github.com/ansible/ansible/commit/7239d2d371bc6e274cbb7314e01431adce6ae25a
- https://github.com/ansible/ansible/commit/fea130480d261ea5bf6fcd5cf19a348f1686ceb1
- https://access.redhat.com/errata/RHSA-2023:7773
- https://access.redhat.com/security/cve/CVE-2023-5764
- https://bugzilla.redhat.com/show_bug.cgi?id=2247629
- https://github.com/ansible/ansible
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X7Q6CHPVCHMZS5M7V22GOKFSXZAQ24EU
