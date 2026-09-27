# [H] media: uvcvideo: Remove dangling pointers

## Summary
Severity: High
Advisory: CVE-2024-58002
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58002
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: uvcvideo: Remove dangling pointers

When an async control is written, we copy a pointer to the file handle
that started the operation. That pointer will be used when the device is
done. Which could be anytime in the future.

If the user closes that file descriptor, its structure will be freed,
and there will be one dangling pointer per pending async control, that
the driver will try to use.

Clean all the dangling pointers during release().

To avoid adding a performance penalty in the most common case (no async
operation), a counter has been introduced with some logic to make sure
that it is properly handled.

## References
- https://git.kernel.org/stable/c/117f7a2975baa4b7d702d3f4830d5a4ebd0c6d50
- https://git.kernel.org/stable/c/221cd51efe4565501a3dbf04cc011b537dcce7fb
- https://git.kernel.org/stable/c/2a29413ace64627e178fd422dd8a5d95219a2c0b
- https://git.kernel.org/stable/c/438bda062b2c40ddd7df23b932e29ffe0a448cac
- https://git.kernel.org/stable/c/4dbaa738c583a0e947803c69e8996e88cf98d971
- https://git.kernel.org/stable/c/653993f46861f2971e95e9a0e36a34b49dec542c
- https://git.kernel.org/stable/c/9edc7d25f7e49c33a1ce7a5ffadea2222065516c
- https://git.kernel.org/stable/c/ac18d781466252cd35a3e311e0a4b264260fd927
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58002.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58002
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
