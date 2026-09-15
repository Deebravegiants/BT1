# [M] Qemu-kvm: usb: assertion failure in usb_ep_get()

## Summary
Severity: Medium
Advisory: CVE-2024-8354
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-19
Source: https://osv.dev/vulnerability/CVE-2024-8354
Type: osv

## Details
A flaw was found in QEMU. An assertion failure was present in the usb_ep_get() function in hw/net/core.c when trying to get the USB endpoint from a USB device. This flaw may allow a malicious unprivileged guest user to crash the QEMU process on the host and cause a denial of service condition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2024-8354
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8354.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8354
- https://security.netapp.com/advisory/ntap-20241011-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=2313497
- https://gitlab.com/qemu-project/qemu
