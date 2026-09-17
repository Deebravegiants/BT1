# [H] HID: wacom: Fix OOB write in wacom_hid_set_device_mode()

## Summary
Severity: High
Advisory: CVE-2026-63916
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63916
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: wacom: Fix OOB write in wacom_hid_set_device_mode()

wacom_hid_set_device_mode() currently assumes that the HID_DG_INPUTMODE
usage is always located in the first field (field[0]) of the feature report.
However, a device can specify HID_DG_INPUTMODE in a different field.

If HID_DG_INPUTMODE is in a field other than the first one and the first
field has a report_count smaller than the usage_index of HID_DG_INPUTMODE,
this leads to an out-of-bounds write to r->field[0]->value.

Fix this by storing the field index of HID_DG_INPUTMODE in 'struct
hid_data' during feature mapping.  In wacom_hid_set_device_mode(), use
this stored field index to access the correct field and add bounds
checks to ensure both the field index and the value index are within
valid ranges before writing.

## References
- https://git.kernel.org/stable/c/2add311d99646c9d235b2c44f9c169ba30f5db3a
- https://git.kernel.org/stable/c/43e7c02d6090a82fd60d63491f6871aec906345e
- https://git.kernel.org/stable/c/5716a293fb19d382ca2336e08fd28a619a5f3c25
- https://git.kernel.org/stable/c/5db3fca0cec7b33bc5379411d0a60d792c9f9bc0
- https://git.kernel.org/stable/c/83bd8a5756a3c4a413ed8f6253f9eb2821e1ccaf
- https://git.kernel.org/stable/c/b8338111e14183972359009c12d0dbd81d2e1e16
- https://git.kernel.org/stable/c/c0a8899e02ddebd51e2589835182c239c2e224ae
- https://git.kernel.org/stable/c/ed598de9f61582902406d352d99f2073d8e00298
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63916.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63916
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
