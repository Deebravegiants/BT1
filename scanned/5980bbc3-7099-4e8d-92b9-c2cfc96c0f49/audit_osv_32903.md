# [H] HID: wacom: fix crash in wacom_aes_battery_handler()

## Summary
Severity: High
Advisory: CVE-2025-38253
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38253
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: wacom: fix crash in wacom_aes_battery_handler()

Commit fd2a9b29dc9c ("HID: wacom: Remove AES power_supply after extended
inactivity") introduced wacom_aes_battery_handler() which is scheduled
as a delayed work (aes_battery_work).

In wacom_remove(), aes_battery_work is not canceled. Consequently, if
the device is removed while aes_battery_work is still pending, then hard
crashes or "Oops: general protection fault..." are experienced when
wacom_aes_battery_handler() is finally called. E.g., this happens with
built-in USB devices after resume from hibernate when aes_battery_work
was still pending at the time of hibernation.

So, take care to cancel aes_battery_work in wacom_remove().

## References
- https://git.kernel.org/stable/c/57a3d82200dbeccd002244b96acad570eeeb731f
- https://git.kernel.org/stable/c/a4f182ffa30c52ad1c8e12edfb8049ee748c0f1b
- https://git.kernel.org/stable/c/f3054152c12e2eed1e72704aff47b0ea58229584
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38253.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
