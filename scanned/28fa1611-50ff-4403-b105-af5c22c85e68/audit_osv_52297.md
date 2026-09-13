# [M] CVE-2021-47298

## Summary
Severity: Medium
Advisory: CVE-2021-47298
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47298
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Fix potential memory leak on unlikely error case

If skb_linearize is needed and fails we could leak a msg on the error
handling. To fix ensure we kfree the msg block before returning error.
Found during code review.

## References
- https://git.kernel.org/stable/c/7e6b27a69167f97c56b5437871d29e9722c3e470
- https://git.kernel.org/stable/c/6c508a1c6c62793dc6e6872cad4b200097bab7c9
- https://git.kernel.org/stable/c/715f378f42909c401ec043f5150c4fdf57fb8889
