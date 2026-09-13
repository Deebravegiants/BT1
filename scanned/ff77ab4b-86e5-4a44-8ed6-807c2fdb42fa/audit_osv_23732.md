# [H] staging: r8188eu: prevent ->Ssid overflow in rtw_wx_set_scan()

## Summary
Severity: High
Advisory: CVE-2022-49405
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49405
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: r8188eu: prevent ->Ssid overflow in rtw_wx_set_scan()

This code has a check to prevent read overflow but it needs another
check to prevent writing beyond the end of the ->Ssid[] array.

## References
- https://git.kernel.org/stable/c/476bfda0be0f9669add92bff604ca78226cf53d1
- https://git.kernel.org/stable/c/ac2eab7de458f5e1210ce1237afab40a307075c8
- https://git.kernel.org/stable/c/bc10916e890948d8927a5c8c40fb5dc44be5e1b8
- https://git.kernel.org/stable/c/c4bd6b72df4f01aa866ceb298466d6d07a6bd525
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49405.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49405
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
