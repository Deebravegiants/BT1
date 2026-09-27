# [H] JLSEC-2026-492

## Summary
Severity: High
Advisory: JLSEC-2026-492
Ecosystem: Julia
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/JLSEC-2026-492
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.101+0

## Details
A security vulnerability has been detected in libssh2 up to 1.11.1. The impacted element is the function `userauth_password` of the file `src/userauth.c`. Such manipulation of the argument `username_len/password_len` leads to integer overflow. The attack may be launched remotely. The name of the patch is 256d04b60d80bf1190e96b0ad1e91b2174d744b1. A patch should be applied to remediate this issue.

## References
- https://access.redhat.com/errata/RHSA-2026:16736
- https://access.redhat.com/errata/RHSA-2026:7021
- https://access.redhat.com/security/cve/CVE-2026-7598
- https://bugzilla.redhat.com/show_bug.cgi?id=2464597
- https://github.com/libssh2/libssh2/
- https://github.com/libssh2/libssh2/commit/256d04b60d80bf1190e96b0ad1e91b2174d744b1
- https://github.com/libssh2/libssh2/pull/1858
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-7598.json
- https://vuldb.com/submit/805564
- https://vuldb.com/vuln/360555
- https://vuldb.com/vuln/360555/cti
