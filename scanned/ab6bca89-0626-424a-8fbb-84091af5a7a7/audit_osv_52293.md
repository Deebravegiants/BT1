# [M] CVE-2021-47294

## Summary
Severity: Medium
Advisory: CVE-2021-47294
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47294
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

netrom: Decrease sock refcount when sock timers expire

Commit 63346650c1a9 ("netrom: switch to sock timer API") switched to use
sock timer API. It replaces mod_timer() by sk_reset_timer(), and
del_timer() by sk_stop_timer().

Function sk_reset_timer() will increase the refcount of sock if it is
called on an inactive timer, hence, in case the timer expires, we need to
decrease the refcount ourselves in the handler, otherwise, the sock
refcount will be unbalanced and the sock will never be freed.

## References
- https://git.kernel.org/stable/c/bc1660206c3723c37ed4d622ad81781f1e987250
- https://git.kernel.org/stable/c/25df44e90ff5959b5c24ad361b648504a7e39ef3
- https://git.kernel.org/stable/c/48866fd5c361ea417ed24b43fc2a7dc2f5b060ef
- https://git.kernel.org/stable/c/517a16b1a88bdb6b530f48d5d153478b2552d9a8
- https://git.kernel.org/stable/c/6811744bd0efb9e472cb15d066cdb460beb8cb8a
- https://git.kernel.org/stable/c/853262355518cd1247515b74e83fabf038aa6c29
- https://git.kernel.org/stable/c/9619cc7d97c3aa8ed3cfd2b8678b74fb6d6c7950
- https://git.kernel.org/stable/c/a01634bf91f2b6c42583770eb6815fb6d1e251cf
