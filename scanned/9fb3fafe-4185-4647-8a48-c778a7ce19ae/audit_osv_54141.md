# [M] CVE-2023-4010

## Summary
Severity: Medium
Advisory: CVE-2023-4010
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-31
Source: https://osv.dev/vulnerability/CVE-2023-4010
Type: osv

## Details
A flaw was found in the USB Host Controller Driver framework in the Linux kernel. The usb_giveback_urb function has a logic loophole in its implementation. Due to the inappropriate judgment condition of the goto statement, the function cannot return under the input of a specific malformed descriptor file, so it falls into an endless loop, resulting in a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-4010
- https://bugzilla.redhat.com/show_bug.cgi?id=2227726
- https://github.com/wanrenmi/a-usb-kernel-bug
