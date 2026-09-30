# [C] CVE-2018-20718

## Summary
Severity: Critical
Advisory: CVE-2018-20718
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2018-20718
Type: osv

## Details
In Pydio before 8.2.2, an attack is possible via PHP Object Injection because a user is allowed to use the $phpserial$a:0:{} syntax to store a preference. An attacker either needs a "public link" of a file, or access to any unprivileged user account for creation of such a link.

## References
- https://blog.ripstech.com/2018/pydio-unauthenticated-remote-code-execution/
