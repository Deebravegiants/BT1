# [H] CVE-2017-18284

## Summary
Severity: High
Advisory: CVE-2017-18284
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2017-18284
Type: osv

## Details
The Gentoo app-backup/burp package before 2.1.32 sets the ownership of the PID file directory to the burp account, which might allow local users to kill arbitrary processes by leveraging access to this account for PID file modification before a root script sends a SIGKILL.

## References
- https://security.gentoo.org/glsa/201806-03
- https://bugs.gentoo.org/628770
