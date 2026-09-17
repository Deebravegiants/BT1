# [C] Ansible fails to properly sanitize fact variables sent from the Ansible controller

## Summary
Severity: Critical
Advisory: GHSA-jg4f-jqm5-4mgq
CVE: CVE-2016-8628
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-jg4f-jqm5-4mgq
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.2.0.0

## Details
Ansible before version 2.2.0 fails to properly sanitize fact variables sent from the Ansible controller. An attacker with the ability to create special variables on the controller could execute arbitrary commands on Ansible clients as the user Ansible runs as.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8628
- https://github.com/ansible/ansible/issues/41903
- https://github.com/ansible/ansible/commit/35938b907dfcd1106ca40b794f0db446bdb8cf09
- https://access.redhat.com/errata/RHSA-2016:2778
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8628
- https://github.com/advisories/GHSA-jg4f-jqm5-4mgq
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-38.yaml
- https://web.archive.org/web/20200227214455/http://www.securityfocus.com/bid/94109
