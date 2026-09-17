# [M] CVE-2021-47037

## Summary
Severity: Medium
Advisory: CVE-2021-47037
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47037
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: q6afe-clocks: fix reprobing of the driver

Q6afe-clocks driver can get reprobed. For example if the APR services
are restarted after the firmware crash. However currently Q6afe-clocks
driver will oops because hw.init will get cleared during first _probe
call. Rewrite the driver to fill the clock data at runtime rather than
using big static array of clocks.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://git.kernel.org/stable/c/2202e87fc19440cecfd4f7b4f60a7d48bc2e236c
- https://git.kernel.org/stable/c/62413972f5266568848a36fd15160397b211fa74
- https://git.kernel.org/stable/c/6893df3753beafa5f7351228a9dd8157a57d7492
- https://git.kernel.org/stable/c/96fadf7e8ff49fdb74754801228942b67c3eeebd
