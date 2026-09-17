# [H] CVE-2021-47357

## Summary
Severity: High
Advisory: CVE-2021-47357
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47357
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

atm: iphase: fix possible use-after-free in ia_module_exit()

This module's remove path calls del_timer(). However, that function
does not wait until the timer handler finishes. This means that the
timer handler may still be running after the driver's remove function
has finished, which would result in a use-after-free.

Fix by calling del_timer_sync(), which makes sure the timer handler
has finished, and unable to re-schedule itself.

## References
- https://git.kernel.org/stable/c/a832ee2f2145f57443b2d565f8cb5490e8339f42
- https://git.kernel.org/stable/c/b58d246a058ae88484758cd4ab27b3180fd5ecf8
- https://git.kernel.org/stable/c/bcdd2be48edd8c6867fb44112cb8d18086beae29
- https://git.kernel.org/stable/c/d1fb12412874c94ad037e11d0ecdd1140a439297
- https://git.kernel.org/stable/c/e759ff76ebbbfcdcf83b6634c54dc47828573d8b
- https://git.kernel.org/stable/c/1c72e6ab66b9598cac741ed397438a52065a8f1f
- https://git.kernel.org/stable/c/89ce0b0747f319eb70f85bc820dcc43cebbd5417
- https://git.kernel.org/stable/c/9e161687855175334ca93c6c3ccb221731194479
- https://git.kernel.org/stable/c/c9172498d4d62c9b64e5fb37c1ee0343e65fe51b
