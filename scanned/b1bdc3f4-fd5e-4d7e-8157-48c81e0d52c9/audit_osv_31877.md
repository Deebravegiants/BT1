# [H] HID: hid-steam: Fix use-after-free when detaching device

## Summary
Severity: High
Advisory: CVE-2025-21923
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21923
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.79 <6.6.83, >=6.12.16 <6.12.19, >=6.13.4 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: hid-steam: Fix use-after-free when detaching device

When a hid-steam device is removed it must clean up the client_hdev used for
intercepting hidraw access. This can lead to scheduling deferred work to
reattach the input device. Though the cleanup cancels the deferred work, this
was done before the client_hdev itself is cleaned up, so it gets rescheduled.
This patch fixes the ordering to make sure the deferred work is properly
canceled.

## References
- https://git.kernel.org/stable/c/026714ec7546de741826324a6a1914c91024d06c
- https://git.kernel.org/stable/c/a899adf7063c6745aaff1ec869f3c7f6329ed0a1
- https://git.kernel.org/stable/c/e53fc232a65f7488ab75d03a5b95f06aaada7262
- https://git.kernel.org/stable/c/ea3f18d2f02629653b7bfe42607737ccd1343e54
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21923.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21923
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
