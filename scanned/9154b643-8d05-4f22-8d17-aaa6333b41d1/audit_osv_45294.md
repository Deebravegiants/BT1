# [H] A path traversal vulnerability exists in rsync

## Summary
Severity: High
Advisory: JLSEC-2025-326
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-326
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.0+0

## Details
A path traversal vulnerability exists in rsync. It stems from behavior enabled by the `--inc-recursive` option, a default-enabled option for many client options and can be enabled by the server even if not explicitly enabled by the client. When using the `--inc-recursive` option, a lack of proper symlink verification coupled with deduplication checks occurring on a per-file-list basis could allow a server to write files outside of the client's intended destination directory. A malicious server could write malicious files to arbitrary locations named after valid directories/paths on the client.

## References
- https://access.redhat.com/errata/RHBA-2025:6470
- https://access.redhat.com/errata/RHSA-2025:23154
- https://access.redhat.com/errata/RHSA-2025:23235
- https://access.redhat.com/errata/RHSA-2025:23407
- https://access.redhat.com/errata/RHSA-2025:23415
- https://access.redhat.com/errata/RHSA-2025:23416
- https://access.redhat.com/errata/RHSA-2025:23842
- https://access.redhat.com/errata/RHSA-2025:23853
- https://access.redhat.com/errata/RHSA-2025:23854
- https://access.redhat.com/errata/RHSA-2025:23858
- https://access.redhat.com/errata/RHSA-2025:2600
- https://access.redhat.com/errata/RHSA-2025:7050
- https://access.redhat.com/errata/RHSA-2025:8385
- https://access.redhat.com/security/cve/CVE-2024-12087
- https://bugzilla.redhat.com/show_bug.cgi?id=2330672
- https://github.com/google/security-research/security/advisories/GHSA-p5pg-x43v-mvqj
- https://kb.cert.org/vuls/id/952657
- https://lists.debian.org/debian-lts-announce/2025/01/msg00008.html
- https://security.netapp.com/advisory/ntap-20250131-0002/
- https://www.kb.cert.org/vuls/id/952657
