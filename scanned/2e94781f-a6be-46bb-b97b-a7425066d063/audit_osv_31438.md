# [H] Qemu-kvm: vnc websocket handshake use-after-free

## Summary
Severity: High
Advisory: CVE-2025-11234
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-11234
Type: osv

## Details
A flaw was found in QEMU. If the QIOChannelWebsock object is freed while it is waiting to complete a handshake, a GSource is leaked. This can lead to the callback firing later on and triggering a use-after-free in the use of the channel. This can be abused by a malicious client with network access to the VNC WebSocket port to cause a denial of service during the WebSocket handshake prior to the VNC client authentication.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:23228
- https://access.redhat.com/errata/RHSA-2026:0326
- https://access.redhat.com/errata/RHSA-2026:0332
- https://access.redhat.com/errata/RHSA-2026:0702
- https://access.redhat.com/errata/RHSA-2026:1831
- https://access.redhat.com/errata/RHSA-2026:18772
- https://access.redhat.com/errata/RHSA-2026:22147
- https://access.redhat.com/errata/RHSA-2026:3077
- https://access.redhat.com/errata/RHSA-2026:3165
- https://access.redhat.com/errata/RHSA-2026:5578
- https://access.redhat.com/errata/RHSA-2026:59831
- https://access.redhat.com/security/cve/CVE-2025-11234
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11234.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-11234
- https://bugzilla.redhat.com/show_bug.cgi?id=2401209
- https://gitlab.com/qemu-project/qemu
