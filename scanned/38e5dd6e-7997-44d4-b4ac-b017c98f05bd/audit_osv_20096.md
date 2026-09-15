# [M] CVE-2021-3027

## Summary
Severity: Medium
Advisory: CVE-2021-3027
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-3027
Type: osv

## Details
app/views_mod/user/user.py in LibrIT PaSSHport through 2.5 is affected by LDAP Injection. There is an information leak through the crafting of special queries, escaping the provided search filter because user input gets no sanitization.

## References
- https://jorgectf.gitlab.io/disclosure/cve-2021-3027/
- https://github.com/LibrIT/passhport/commit/366b03f607729c4538e91b634ecc57c8398522a1
- https://github.com/LibrIT/passhport/pull/562
