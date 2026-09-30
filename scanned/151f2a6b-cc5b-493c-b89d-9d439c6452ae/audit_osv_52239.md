# [H] CVE-2021-47232

## Summary
Severity: High
Advisory: CVE-2021-47232
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47232
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: j1939: fix Use-after-Free, hold skb ref while in use

This patch fixes a Use-after-Free found by the syzbot.

The problem is that a skb is taken from the per-session skb queue,
without incrementing the ref count. This leads to a Use-after-Free if
the skb is taken concurrently from the session queue due to a CTS.

## References
- https://git.kernel.org/stable/c/2030043e616cab40f510299f09b636285e0a3678
- https://git.kernel.org/stable/c/22cba878abf646cd3a02ee7c8c2cef7afe66a256
- https://git.kernel.org/stable/c/509ab6bfdd0c76daebbad0f0af07da712116de22
- https://git.kernel.org/stable/c/1071065eeb33d32b7d98c2ce7591881ae7381705
