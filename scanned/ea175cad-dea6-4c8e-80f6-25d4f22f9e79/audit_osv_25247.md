# [M] Qemu: vnc: infinite loop in inflate_buffer() leads to denial of service

## Summary
Severity: Medium
Advisory: CVE-2023-3255
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-13
Source: https://osv.dev/vulnerability/CVE-2023-3255
Type: osv

## Details
A flaw was found in the QEMU built-in VNC server while processing ClientCutText messages. A wrong exit condition may lead to an infinite loop when inflating an attacker controlled zlib buffer in the `inflate_buffer` function. This could allow a remote authenticated client who is able to send a clipboard to the VNC server to trigger a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:2135
- https://access.redhat.com/errata/RHSA-2024:2962
- https://access.redhat.com/security/cve/CVE-2023-3255
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3255.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3255
- https://security.netapp.com/advisory/ntap-20231020-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=2218486
