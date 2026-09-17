# [M] Libssh: integer overflow in libssh sftp server packet length validation leading to denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-5449
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-5449
Type: osv

## Details
A flaw was found in the SFTP server message decoding logic of libssh. The issue occurs due to an incorrect packet length check that allows an integer overflow when handling large payload sizes on 32-bit systems. This issue leads to failed memory allocation and causes the server process to crash, resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=261612179f740bc62ba363d98b3bd5e5573a811f
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=3443aec90188d6aab9282afc80a81df5ab72c4da
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=5504ff40515439a5fecbb17da7483000c4d12eb7
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=78485f446af9b30e37eb8f177b81940710d54496
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=f79ec51b7fd519dbc5737a7ba826e3ed093f6ceb
- https://www.libssh.org
- https://access.redhat.com/security/cve/CVE-2025-5449
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5449.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5449
- https://www.libssh.org/security/advisories/CVE-2025-5449.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2369705
