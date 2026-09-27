# [H] usb: gadget: u_audio: Fix race condition use of controls after free during gadget unbind.

## Summary
Severity: High
Advisory: CVE-2024-38628
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-38628
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: u_audio: Fix race condition use of controls after free during gadget unbind.

Hang on to the control IDs instead of pointers since those are correctly
handled with locks.

## References
- https://git.kernel.org/stable/c/1b739388aa3f8dfb63a9fca777e6dfa6912d0464
- https://git.kernel.org/stable/c/453d3fa9266e53f85377b911c19b9a4563fa88c0
- https://git.kernel.org/stable/c/89e66809684485590ea0b32c3178e42cba36ac09
- https://git.kernel.org/stable/c/bea73b58ab67fe581037ad9cdb93c2557590c068
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38628.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38628
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
