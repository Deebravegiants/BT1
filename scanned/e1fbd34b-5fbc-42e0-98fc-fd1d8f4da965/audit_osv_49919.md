# [H] CVE-2019-3466

## Summary
Severity: High
Advisory: CVE-2019-3466
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-20
Source: https://osv.dev/vulnerability/CVE-2019-3466
Type: osv

## Details
The pg_ctlcluster script in postgresql-common in versions prior to 210 didn't drop privileges when creating socket/statistics temporary directories, which could result in local privilege escalation.

## References
- https://usn.ubuntu.com/4194-2/
- https://blog.mirch.io/2019/11/15/cve-2019-3466-debian-ubuntu-pg_ctlcluster-privilege-escalation/
