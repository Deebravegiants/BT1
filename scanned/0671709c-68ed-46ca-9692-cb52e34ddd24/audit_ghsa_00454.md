# [C] Ansible is vulnerable to an improper input validation in Ansible's handling of data sent from client systems

## Summary
Severity: Critical
Advisory: GHSA-m956-frf4-m2wr
CVE: CVE-2016-9587
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-m956-frf4-m2wr
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.1.4.0
- PyPI: `ansible` — affected >=2.2.0.0 <2.2.1.0

## Details
Ansible before versions 2.1.4.0, 2.2.1.0 is vulnerable to an improper input validation in Ansible's handling of data sent from client systems. An attacker with control over a client system being managed by Ansible and the ability to send facts back to the Ansible server could use this flaw to execute arbitrary code on the Ansible server using the Ansible server privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9587
- https://access.redhat.com/errata/RHSA-2017:0448
- https://access.redhat.com/errata/RHSA-2017:0515
- https://access.redhat.com/errata/RHSA-2017:1685
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9587
- https://github.com/advisories/GHSA-m956-frf4-m2wr
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-39.yaml
- https://security.gentoo.org/glsa/201701-77
- https://web.archive.org/web/20170115210655/http://www.securityfocus.com/bid/95352
- https://www.exploit-db.com/exploits/41013
- http://rhn.redhat.com/errata/RHSA-2017-0195.html
- http://rhn.redhat.com/errata/RHSA-2017-0260.html
