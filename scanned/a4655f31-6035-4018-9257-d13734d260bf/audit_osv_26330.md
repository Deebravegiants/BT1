# [H] platform/x86: wmi: Fix opening of char device

## Summary
Severity: High
Advisory: CVE-2023-52864
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52864
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.299, >=4.20.0 <5.4.261, >=5.5.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: wmi: Fix opening of char device

Since commit fa1f68db6ca7 ("drivers: misc: pass miscdevice pointer via
file private data"), the miscdevice stores a pointer to itself inside
filp->private_data, which means that private_data will not be NULL when
wmi_char_open() is called. This might cause memory corruption should
wmi_char_open() be unable to find its driver, something which can
happen when the associated WMI device is deleted in wmi_free_devices().

Fix the problem by using the miscdevice pointer to retrieve the WMI
device data associated with a char device using container_of(). This
also avoids wmi_char_open() picking a wrong WMI device bound to a
driver with the same name as the original driver.

## References
- https://git.kernel.org/stable/c/36d85fa7ae0d6be651c1a745191fa7ef055db43e
- https://git.kernel.org/stable/c/44a96796d25809502c75771d40ee693c2e44724e
- https://git.kernel.org/stable/c/9fb0eed09e1470cd4021ff52b2b9dfcbcee4c203
- https://git.kernel.org/stable/c/cf098e937dd125c0317a0d6f261ac2a950a233d6
- https://git.kernel.org/stable/c/d426a2955e45a95b2282764105fcfb110a540453
- https://git.kernel.org/stable/c/e0bf076b734a2fab92d8fddc2b8b03462eee7097
- https://git.kernel.org/stable/c/eba9ac7abab91c8f6d351460239108bef5e7a0b6
- https://git.kernel.org/stable/c/fb7b06b59c6887659c6ed0ecd3110835eecbb6a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52864.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52864
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
