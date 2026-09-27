# [M] CVE-2021-47150

## Summary
Severity: Medium
Advisory: CVE-2021-47150
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47150
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fec: fix the potential memory leak in fec_enet_init()

If the memory allocated for cbd_base is failed, it should
free the memory allocated for the queues, otherwise it causes
memory leak.

And if the memory allocated for the queues is failed, it can
return error directly.

## References
- https://git.kernel.org/stable/c/15102886bc8f5f29daaadf2d925591d564c17e9f
- https://git.kernel.org/stable/c/20255d41ac560397b6a07d8d87dcc5e2efc7672a
- https://git.kernel.org/stable/c/32a1777fd113335c3f70dc445dffee0ad1c6870f
- https://git.kernel.org/stable/c/619fee9eb13b5d29e4267cb394645608088c28a8
- https://git.kernel.org/stable/c/8ee7ef4a57a9e1228b6f345aaa70aa8951c7e9cd
