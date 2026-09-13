# [H] Improper i/o watch removal in tls handshake can lead to remote unauthenticated denial of service

## Summary
Severity: High
Advisory: CVE-2023-3354
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-11
Source: https://osv.dev/vulnerability/CVE-2023-3354
Type: osv

## Details
A flaw was found in the QEMU built-in VNC server. When a client connects to the VNC server, QEMU checks whether the current number of connections crosses a certain threshold and if so, cleans up the previous connection. If the previous connection happens to be in the handshake phase and fails, QEMU cleans up the connection again, resulting in a NULL pointer dereference issue. This could allow a remote unauthenticated client to cause a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MURWGXDIF2WTDXV36T6HFJDBL632AO7R/
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-3354
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3354.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3354
- https://bugzilla.redhat.com/show_bug.cgi?id=2216478
