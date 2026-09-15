# [M] CVE-2020-8446

## Summary
Severity: Medium
Advisory: CVE-2020-8446
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-30
Source: https://osv.dev/vulnerability/CVE-2020-8446
Type: osv

## Details
In OSSEC-HIDS 2.7 through 3.5.0, the server component responsible for log analysis (ossec-analysisd) is vulnerable to path traversal (with write access) via crafted syscheck messages written directly to the analysisd UNIX domain socket by a local user.

## References
- https://github.com/ossec/ossec-hids/issues/1821
- https://security.gentoo.org/glsa/202007-33
- https://www.ossec.net/
- https://github.com/ossec/ossec-hids/issues/1813
