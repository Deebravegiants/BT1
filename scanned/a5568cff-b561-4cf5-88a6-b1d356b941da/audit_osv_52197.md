# [M] CVE-2021-47186

## Summary
Severity: Medium
Advisory: CVE-2021-47186
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47186
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: check for null after calling kmemdup

kmemdup can return a null pointer so need to check for it, otherwise
the null key will be dereferenced later in tipc_crypto_key_xmit as
can be seen in the trace [1].


[1] https://syzkaller.appspot.com/bug?id=bca180abb29567b189efdbdb34cbf7ba851c2a58

## References
- https://git.kernel.org/stable/c/3e6db079751afd527bf3db32314ae938dc571916
- https://git.kernel.org/stable/c/9404c4145542c23019a80ab1bb2ecf73cd057b10
- https://git.kernel.org/stable/c/a7d91625863d4ffed63b993b5e6dc1298b6430c9
