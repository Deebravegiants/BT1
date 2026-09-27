# [H] HID: elan: Fix potential double free in elan_input_configured

## Summary
Severity: High
Advisory: CVE-2022-49508
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49508
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: elan: Fix potential double free in elan_input_configured

'input' is a managed resource allocated with devm_input_allocate_device(),
so there is no need to call input_free_device() explicitly or
there will be a double free.

According to the doc of devm_input_allocate_device():
 * Managed input devices do not need to be explicitly unregistered or
 * freed as it will be done automatically when owner device unbinds from
 * its driver (or binding fails).

## References
- https://git.kernel.org/stable/c/1af20714fedad238362571620be0bd690ded05b6
- https://git.kernel.org/stable/c/24f9dfdaece9bd75bb8dbfdba83eddeefdf7dc47
- https://git.kernel.org/stable/c/5291451851feeb66fd4bf0826710f482f3b1ab38
- https://git.kernel.org/stable/c/6d0726725c7c560495f5ff364862a2cefea542e3
- https://git.kernel.org/stable/c/8bb1716507ebf12d50bbf181764481de3b6bc7fd
- https://git.kernel.org/stable/c/c92ec22a991778a096342cf1a917ae36c5c86a90
- https://git.kernel.org/stable/c/f1d4f19a796551edc6679a681ea1756b8c578c08
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49508.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49508
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
