# [H] A flaw was found in rsync

## Summary
Severity: High
Advisory: JLSEC-2025-327
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-327
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.0+0

## Details
A flaw was found in rsync. When using the `--safe-links` option, the rsync client fails to properly verify if a symbolic link destination sent from the server contains another symbolic link within it. This results in a path traversal vulnerability, which may lead to arbitrary file write outside the desired directory.

## References
- https://access.redhat.com/errata/RHBA-2025:6470
- https://access.redhat.com/errata/RHSA-2025:2600
- https://access.redhat.com/errata/RHSA-2025:7050
- https://access.redhat.com/errata/RHSA-2025:8385
- https://access.redhat.com/security/cve/CVE-2024-12088
- https://bugzilla.redhat.com/show_bug.cgi?id=2330676
- https://github.com/google/security-research/security/advisories/GHSA-p5pg-x43v-mvqj
- https://kb.cert.org/vuls/id/952657
- https://lists.debian.org/debian-lts-announce/2025/01/msg00008.html
- https://security.netapp.com/advisory/ntap-20250131-0002/
- https://www.kb.cert.org/vuls/id/952657
