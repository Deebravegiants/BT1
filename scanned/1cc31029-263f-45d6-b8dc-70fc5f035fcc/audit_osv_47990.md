# [M] CVE-2017-16534

## Summary
Severity: Medium
Advisory: CVE-2017-16534
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16534
Type: osv

## Details
The cdc_parse_cdc_header function in drivers/usb/core/message.c in the Linux kernel before 4.13.6 allows local users to cause a denial of service (out-of-bounds read and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- https://groups.google.com/d/msg/syzkaller/nXnjqI73uPo/6sUyq6kqAgAJ
- https://github.com/torvalds/linux/commit/2e1c42391ff2556387b3cb6308b24f6f65619feb
