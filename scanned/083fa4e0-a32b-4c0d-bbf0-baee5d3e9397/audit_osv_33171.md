# [H] platform/x86: asus-wmi: Fix racy registrations

## Summary
Severity: High
Advisory: CVE-2025-39837
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39837
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: asus-wmi: Fix racy registrations

asus_wmi_register_driver() may be called from multiple drivers
concurrently, which can lead to the racy list operations, eventually
corrupting the memory and hitting Oops on some ASUS machines.
Also, the error handling is missing, and it forgot to unregister ACPI
lps0 dev ops in the error case.

This patch covers those issues by introducing a simple mutex at
acpi_wmi_register_driver() & *_unregister_driver, and adding the
proper call of asus_s2idle_check_unregister() in the error path.

## References
- https://git.kernel.org/stable/c/5549202b9c02c2ecbc8634768a3da8d9e82d548d
- https://git.kernel.org/stable/c/e7a70326fb26b905cfc8fe2366113aa4394733ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39837.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39837
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
