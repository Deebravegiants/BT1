# [H] CVE-2020-36657

## Summary
Severity: High
Advisory: CVE-2020-36657
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/CVE-2020-36657
Type: osv

## Details
uptimed before 0.4.6-r1 on Gentoo allows local users (with access to the uptimed user account) to gain root privileges by creating a hard link within the /var/spool/uptimed directory, because there is an unsafe chown -R call.

## References
- https://security.gentoo.org/glsa/202305-14
- https://bugs.gentoo.org/630810
