# [H] HID: playstation: Clamp num_touch_reports

## Summary
Severity: High
Advisory: CVE-2026-46232
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46232
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: playstation: Clamp num_touch_reports

A device would never lie about the number of touch reports would it?

If it does the loop in dualshock4_parse_report will read off the end of
the touch_reports array, up to about 2 KiB for the maximum number of 256
loop iteraions. The data that is read is emitted via evdev if the
DS4_TOUCH_POINT_INACTIVE bit happens to be set. Protect against this by
clamping the num_touch_reports value provided by the device to the
maximum size of the touch_reports array.

## References
- https://git.kernel.org/stable/c/0bc4cf1a6ba00fb8c074531b179bc7b97502fbc4
- https://git.kernel.org/stable/c/208f6d5b1dfd6399bc6af9e11f27f1f496243ed0
- https://git.kernel.org/stable/c/7812694752a5f295eaa05a093b90a2c332666051
- https://git.kernel.org/stable/c/9c031b24aed6733b6dcc5d98527875b8654a04e9
- https://git.kernel.org/stable/c/cac61b58a3b6340c52afa06bb15eac033158db2f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46232.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
