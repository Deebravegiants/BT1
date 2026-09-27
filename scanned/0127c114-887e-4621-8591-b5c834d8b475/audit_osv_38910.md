# [H] HID: multitouch: Check to ensure report responses match the request

## Summary
Severity: High
Advisory: CVE-2026-43047
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43047
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: multitouch: Check to ensure report responses match the request

It is possible for a malicious (or clumsy) device to respond to a
specific report's feature request using a completely different report
ID.  This can cause confusion in the HID core resulting in nasty
side-effects such as OOB writes.

Add a check to ensure that the report ID in the response, matches the
one that was requested.  If it doesn't, omit reporting the raw event and
return early.

## References
- https://git.kernel.org/stable/c/2edc92f89eee328b5be5706b5d431bf90669e9c0
- https://git.kernel.org/stable/c/516da3f25cfe18643835af1cf09b0e9ffc36c383
- https://git.kernel.org/stable/c/6a4acd3e86fe5584050c213d95147eba33856033
- https://git.kernel.org/stable/c/74c6015375d8b9bc1b1eb79f20636c8e894bcad7
- https://git.kernel.org/stable/c/7f66fdbc077faed3b52519228d21d81979e92249
- https://git.kernel.org/stable/c/a61163daf8a90b4a7ef154d5fc9c525f665734e3
- https://git.kernel.org/stable/c/c7a27bb4d0f6573ca0f9c7ef0b63291486239190
- https://git.kernel.org/stable/c/e716edafedad4952fe3a4a273d2e039a84e8681a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43047.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43047
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
