# [H] CVE-2018-20969

## Summary
Severity: High
Advisory: CVE-2018-20969
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-16
Source: https://osv.dev/vulnerability/CVE-2018-20969
Type: osv

## Details
do_ed_script in pch.c in GNU patch through 2.7.6 does not block strings beginning with a ! character. NOTE: this is the same commit as for CVE-2019-13638, but the ! syntax is specific to ed, and is unrelated to a shell metacharacter.

## References
- http://packetstormsecurity.com/files/154124/GNU-patch-Command-Injection-Directory-Traversal.html
- https://access.redhat.com/errata/RHSA-2019:2798
- https://access.redhat.com/errata/RHSA-2019:2964
- https://access.redhat.com/errata/RHSA-2019:3757
- https://access.redhat.com/errata/RHSA-2019:3758
- https://access.redhat.com/errata/RHSA-2019:4061
- https://git.savannah.gnu.org/cgit/patch.git/commit/?id=3fcd042d26d70856e826a42b5f93dc4854d80bf0
- https://seclists.org/bugtraq/2019/Aug/29
- https://github.com/irsl/gnu-patch-vulnerabilities
