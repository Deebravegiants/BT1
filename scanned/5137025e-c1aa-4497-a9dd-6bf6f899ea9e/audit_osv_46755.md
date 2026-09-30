# [H] CVE-2015-1378

## Summary
Severity: High
Advisory: CVE-2015-1378
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2015-1378
Type: osv

## Details
cmdlineopts.clp in grml-debootstrap in Debian 0.54, 0.68.x before 0.68.1, 0.7x before 0.78 is sourced without checking that the local directory is writable by non-root users.

## References
- http://cve.killedkenny.io/cve/CVE-2015-1378
- http://www.openwall.com/lists/oss-security/2015/01/27/17
- https://github.com/grml/grml-debootstrap/issues/59
- https://people.canonical.com/~ubuntu-security/cve/2015/CVE-2015-1378.html
- https://security-tracker.debian.org/tracker/CVE-2015-1378/
- http://www.openwall.com/lists/oss-security/2015/01/27/17
- https://github.com/grml/grml-debootstrap/issues/59
