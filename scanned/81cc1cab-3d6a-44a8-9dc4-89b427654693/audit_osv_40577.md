# [H] libgit2 - Unauthenticated network-reachable heap out-of-bounds read in transports/smart_pkt.c:set_data

## Summary
Severity: High
Advisory: CVE-2026-53587
Aliases: GHSA-pm24-4jhq-3xvm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-53587
Type: osv

## Details
libgit2 is a portable C implementation of the Git core methods provided as a linkable library with a solid API, allowing to build Git functionality into your application. Prior to 1.8.6 and 1.9.5, libgit2 performs a fixed-size strncmp in set_data in src/libgit2/transports/smart_pkt.c without first verifying that the smart-protocol pkt-line capability buffer contains 14 bytes. A malicious Git server can make bytes after the pkt-line complete object-format=, causing format_str to advance beyond the pkt-line and the following memchr length calculation to underflow. The resulting heap out-of-bounds walk can crash a client during the first refs-advertisement packet over HTTP, HTTPS, SSH, or the Git protocol. This issue is fixed in versions 1.8.6 and 1.9.5.

## References
- https://github.com/libgit2/libgit2/releases/tag/v1.8.6
- https://github.com/libgit2/libgit2/releases/tag/v1.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53587.json
- https://github.com/libgit2/libgit2/security/advisories/GHSA-pm24-4jhq-3xvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53587
- https://github.com/libgit2/libgit2/commit/2c0ce8c0132ac38ab0db28239462a671e2e5440e
- https://github.com/libgit2/libgit2/commit/affda60c10fcef16723451c0d7dc71b71dc20ad3
- https://github.com/libgit2/libgit2/commit/d7a9fb87f504434e9f45228678953c4fa56e7640
