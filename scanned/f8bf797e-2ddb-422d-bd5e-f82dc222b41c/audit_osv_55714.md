# [H] CVE-2026-4111

## Summary
Severity: High
Advisory: CVE-2026-4111
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-4111
Type: osv

## Details
A flaw was identified in the RAR5 archive decompression logic of the libarchive library, specifically within the archive_read_data() processing path. When a specially crafted RAR5 archive is processed, the decompression routine may enter a state where internal logic prevents forward progress. This condition results in an infinite loop that continuously consumes CPU resources. Because the archive passes checksum validation and appears structurally valid, affected applications cannot detect the issue before processing. This can allow attackers to cause persistent denial-of-service conditions in services that automatically process archives.

## References
- https://access.redhat.com/security/cve/CVE-2026-4111
- https://bugzilla.redhat.com/show_bug.cgi?id=2446453
- https://github.com/libarchive/libarchive/pull/2877
