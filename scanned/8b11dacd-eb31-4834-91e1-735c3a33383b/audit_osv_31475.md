# [M] Qemu-kvm: stack buffer overflow in e1000 device via short frames in loopback mode

## Summary
Severity: Medium
Advisory: CVE-2025-12464
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/CVE-2025-12464
Type: osv

## Details
A stack-based buffer overflow was found in the QEMU e1000 network device. The code for padding short frames was dropped from individual network devices and moved to the net core code. The issue stems from the device's receive code still being able to process a short frame in loopback mode. This could lead to a buffer overrun in the e1000_receive_iov() function via the loopback code path. A malicious guest user could use this vulnerability to crash the QEMU process on the host, resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-12464
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12464.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-12464
- https://bugzilla.redhat.com/show_bug.cgi?id=2408845
- https://gitlab.com/qemu-project/qemu/-/issues/3043
- https://gitlab.com/qemu-project/qemu
