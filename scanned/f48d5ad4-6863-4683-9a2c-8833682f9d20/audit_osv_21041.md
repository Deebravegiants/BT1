# [C] CVE-2021-40084

## Summary
Severity: Critical
Advisory: CVE-2021-40084
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-25
Source: https://osv.dev/vulnerability/CVE-2021-40084
Type: osv

## Details
opensysusers through 0.6 does not safely use eval on files in sysusers.d that may contain shell metacharacters. For example, it allows command execution via a crafted GECOS field whereas systemd-sysusers (a program with the same specification) does not do that.

## References
- https://github.com/artix-linux/opensysusers/releases
- https://bugs.debian.org/992058
