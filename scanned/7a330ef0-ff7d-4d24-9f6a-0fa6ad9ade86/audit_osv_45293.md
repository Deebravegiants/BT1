# [M] A flaw was found in rsync

## Summary
Severity: Medium
Advisory: JLSEC-2025-325
Ecosystem: Julia
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-325
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.0+0

## Details
A flaw was found in rsync. It could allow a server to enumerate the contents of an arbitrary file from the client's machine. This issue occurs when files are being copied from a client to a server. During this process, the rsync server will send checksums of local data to the client to compare with in order to determine what data needs to be sent to the server. By sending specially constructed checksum values for arbitrary files, an attacker may be able to reconstruct the data of those files byte-by-byte based on the responses from the client.

## References
- https://access.redhat.com/errata/RHBA-2025:6470
- https://access.redhat.com/errata/RHSA-2026:19368
- https://access.redhat.com/errata/RHSA-2026:20603
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/security/cve/CVE-2024-12086
- https://bugzilla.redhat.com/show_bug.cgi?id=2330577
- https://github.com/google/security-research/security/advisories/GHSA-p5pg-x43v-mvqj
- https://kb.cert.org/vuls/id/952657
- https://lists.debian.org/debian-lts-announce/2025/01/msg00008.html
- https://security.netapp.com/advisory/ntap-20250131-0002/
- https://www.kb.cert.org/vuls/id/952657
