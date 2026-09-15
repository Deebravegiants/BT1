# [M] CVE-2021-47248

## Summary
Severity: Medium
Advisory: CVE-2021-47248
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47248
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

udp: fix race between close() and udp_abort()

Kaustubh reported and diagnosed a panic in udp_lib_lookup().
The root cause is udp_abort() racing with close(). Both
racing functions acquire the socket lock, but udp{v6}_destroy_sock()
release it before performing destructive actions.

We can't easily extend the socket lock scope to avoid the race,
instead use the SOCK_DEAD flag to prevent udp_abort from doing
any action when the critical race happens.

Diagnosed-and-tested-by: Kaustubh Pandey <kapandey@codeaurora.org>

## References
- https://git.kernel.org/stable/c/2f73448041bd0682d4b552cfd314ace66107f1ad
- https://git.kernel.org/stable/c/5a88477c1c85e4baa51e91f2d40f2166235daa56
- https://git.kernel.org/stable/c/65310b0aff86980a011c7c7bfa487a333d4ca241
- https://git.kernel.org/stable/c/8729ec8a2238152a4afc212a331a6cd2c61aeeac
- https://git.kernel.org/stable/c/a0882f68f54f7a8b6308261acee9bd4faab5a69e
- https://git.kernel.org/stable/c/a8b897c7bcd47f4147d066e22cc01d1026d7640e
- https://git.kernel.org/stable/c/e3c36c773aed0fef8b1d3d555b43393ec564400f
