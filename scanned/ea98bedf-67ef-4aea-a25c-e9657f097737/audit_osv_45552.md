# [H] JLSEC-2026-13

## Summary
Severity: High
Advisory: JLSEC-2026-13
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/JLSEC-2026-13
Type: osv

## Affected
- Julia: `patch_jll` — affected >=0 <2.8.0+0

## Details
`do_ed_script` in pch.c in GNU patch through 2.7.6 does not block strings beginning with a ! character. NOTE: this is the same commit as for CVE-2019-13638, but the ! syntax is specific to ed, and is unrelated to a shell metacharacter.

## References
- http://packetstormsecurity.com/files/154124/GNU-patch-Command-Injection-Directory-Traversal.html
- https://access.redhat.com/errata/RHSA-2019:2798
- https://access.redhat.com/errata/RHSA-2019:2964
- https://access.redhat.com/errata/RHSA-2019:3757
- https://access.redhat.com/errata/RHSA-2019:3758
- https://access.redhat.com/errata/RHSA-2019:4061
- https://git.savannah.gnu.org/cgit/patch.git/commit/?id=3fcd042d26d70856e826a42b5f93dc4854d80bf0
- https://github.com/irsl/gnu-patch-vulnerabilities
- https://seclists.org/bugtraq/2019/Aug/29
