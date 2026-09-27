# [M] CVE-2021-47093

## Summary
Severity: Medium
Advisory: CVE-2021-47093
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47093
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: intel_pmc_core: fix memleak on registration failure

In case device registration fails during module initialisation, the
platform device structure needs to be freed using platform_device_put()
to properly free all resources (e.g. the device name).

## References
- https://git.kernel.org/stable/c/26a8b09437804fabfb1db080d676b96c0de68e7c
- https://git.kernel.org/stable/c/7a37f2e370699e2feca3dca6c8178c71ceee7e8a
- https://git.kernel.org/stable/c/9ca1324755f1f8629a370af5cc315b175331f5d1
