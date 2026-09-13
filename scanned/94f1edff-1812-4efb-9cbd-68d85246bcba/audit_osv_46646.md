# [C] CVE-2014-4967

## Summary
Severity: Critical
Advisory: CVE-2014-4967
Aliases: GHSA-64cw-m57j-65xj, PYSEC-2020-205
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-18
Source: https://osv.dev/vulnerability/CVE-2014-4967
Type: osv

## Details
Multiple argument injection vulnerabilities in Ansible before 1.6.7 allow remote attackers to execute arbitrary code by leveraging access to an Ansible managed host and providing a crafted fact, as demonstrated by a fact with (1) a trailing " src=" clause, (2) a trailing " temp=" clause, or (3) a trailing " validate=" clause accompanied by a shell command.

## References
- http://www.ocert.org/advisories/ocert-2014-004.html
- https://github.com/ansible/ansible/commit/62a1295a3e08cb6c3e9f1b2a1e6e5dcaeab32527
- https://github.com/ansible/ansible/commit/62a1295a3e08cb6c3e9f1b2a1e6e5dcaeab32527
