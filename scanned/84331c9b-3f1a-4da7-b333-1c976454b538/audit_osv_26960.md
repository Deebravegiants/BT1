# [M] Qemu: vnc: null pointer dereference in qemu_clipboard_request()

## Summary
Severity: Medium
Advisory: CVE-2023-6683
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-6683
Type: osv

## Details
A flaw was found in the QEMU built-in VNC server while processing ClientCutText messages. The qemu_clipboard_request() function can be reached before vnc_server_cut_text_caps() was called and had the chance to initialize the clipboard peer, leading to a NULL pointer dereference. This could allow a malicious authenticated VNC client to crash QEMU and trigger a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:2135
- https://access.redhat.com/errata/RHSA-2024:2962
- https://access.redhat.com/security/cve/CVE-2023-6683
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6683.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6683
- https://security.netapp.com/advisory/ntap-20240223-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2254825
