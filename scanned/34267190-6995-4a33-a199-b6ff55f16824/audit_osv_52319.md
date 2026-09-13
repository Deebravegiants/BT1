# [H] CVE-2021-47324

## Summary
Severity: High
Advisory: CVE-2021-47324
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47324
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

watchdog: Fix possible use-after-free in wdt_startup()

This module's remove path calls del_timer(). However, that function
does not wait until the timer handler finishes. This means that the
timer handler may still be running after the driver's remove function
has finished, which would result in a use-after-free.

Fix by calling del_timer_sync(), which makes sure the timer handler
has finished, and unable to re-schedule itself.

## References
- https://git.kernel.org/stable/c/862f2b5a7c38762ac9e369daefbf361a91aca685
- https://git.kernel.org/stable/c/8adbbe6c86bb13e14f8a19e036ae5f4f5661fd90
- https://git.kernel.org/stable/c/a397cb4576fc2fc802562418b3a50b8f67d60d31
- https://git.kernel.org/stable/c/b4ebf4a4692e84163a69444c70ad515de06e2259
- https://git.kernel.org/stable/c/c08a6b31e4917034f0ed0cb457c3bb209576f542
- https://git.kernel.org/stable/c/0ac50a76cf3cd63db000648b3b19f3f98b8aaa76
- https://git.kernel.org/stable/c/146cc288fb80c662c9c35e7bc58325d1ac0a7875
- https://git.kernel.org/stable/c/dc9403097be52d57a5c9c35efa9be79d166a78af
- https://git.kernel.org/stable/c/63a3dc24bd053792f84cb4eef0168b1266202a02
