# [H] CVE-2020-21665

## Summary
Severity: High
Advisory: CVE-2020-21665
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-17
Source: https://osv.dev/vulnerability/CVE-2020-21665
Type: osv

## Details
In fastadmin V1.0.0.20191212_beta, when a user with administrator rights has logged in, a malicious parameter can be passed for SQL injection in URL /admin/ajax/weigh.

## References
- https://github.com/karsonzhang/fastadmin/commit/e14008ca029d644e2486873fa22629a1d62a7380
