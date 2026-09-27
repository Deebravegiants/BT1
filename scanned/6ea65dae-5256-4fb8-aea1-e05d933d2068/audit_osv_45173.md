# [M] A flaw was found in glib before version 2.63.6

## Summary
Severity: Medium
Advisory: JLSEC-2025-159
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-159
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.68.1+0

## Details
A flaw was found in glib before version 2.63.6. Due to random charset alias, pkexec can leak content from files owned by privileged users to unprivileged ones under the right condition.

## References
- https://access.redhat.com/security/cve/CVE-2021-3800
- https://bugzilla.redhat.com/show_bug.cgi?id=1938284
- https://gitlab.gnome.org/GNOME/glib/-/commit/3529bb4450a51995
- https://lists.debian.org/debian-lts-announce/2022/09/msg00020.html
- https://security.netapp.com/advisory/ntap-20221028-0004/
- https://www.openwall.com/lists/oss-security/2017/06/23/8
