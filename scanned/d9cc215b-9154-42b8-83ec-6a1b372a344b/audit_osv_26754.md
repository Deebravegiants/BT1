# [H] HID: wacom: Use ktime_t rather than int when dealing with timestamps

## Summary
Severity: High
Advisory: CVE-2023-53797
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53797
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.120, >=5.16.0 <6.1.37, >=6.2.0 <6.3.11, >=6.4.0 <6.4.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: wacom: Use ktime_t rather than int when dealing with timestamps

Code which interacts with timestamps needs to use the ktime_t type
returned by functions like ktime_get. The int type does not offer
enough space to store these values, and attempting to use it is a
recipe for problems. In this particular case, overflows would occur
when calculating/storing timestamps leading to incorrect values being
reported to userspace. In some cases these bad timestamps cause input
handling in userspace to appear hung.

## References
- https://git.kernel.org/stable/c/67ce7724637c6adb66f788677cb50b82615de0ac
- https://git.kernel.org/stable/c/9598a647ecc8f300b0540abf9d3b3439859d163b
- https://git.kernel.org/stable/c/99036f1aed7e82773904f5d91a9897bb3e507fd9
- https://git.kernel.org/stable/c/9a6c0e28e215535b2938c61ded54603b4e5814c5
- https://git.kernel.org/stable/c/bdeaa883b765709f231f47f9d6cc76c837a15396
- https://git.kernel.org/stable/c/d0198363f9108e4adb2511e607ba91e44779e8b1
- https://git.kernel.org/stable/c/d89750b19681581796dfbe3689bbb5d439b99b24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53797.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53797
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
