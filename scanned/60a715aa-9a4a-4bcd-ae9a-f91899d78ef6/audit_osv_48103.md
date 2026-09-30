# [H] CVE-2017-18205

## Summary
Severity: High
Advisory: CVE-2017-18205
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2017-18205
Type: osv

## Details
In builtin.c in zsh before 5.4, when sh compatibility mode is used, there is a NULL pointer dereference during processing of the cd command with no argument if HOME is not set.

## References
- https://usn.ubuntu.com/3593-1/
- https://security.gentoo.org/glsa/201805-10
- https://access.redhat.com/errata/RHSA-2018:3073
- https://sourceforge.net/p/zsh/code/ci/eb783754bdb74377f3cea4ceca9c23a02ea1bf58
