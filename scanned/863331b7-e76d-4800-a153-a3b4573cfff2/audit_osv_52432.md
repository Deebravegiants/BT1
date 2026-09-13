# [M] CVE-2021-47443

## Summary
Severity: Medium
Advisory: CVE-2021-47443
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47443
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFC: digital: fix possible memory leak in digital_tg_listen_mdaa()

'params' is allocated in digital_tg_listen_mdaa(), but not free when
digital_send_cmd() failed, which will cause memory leak. Fix it by
freeing 'params' if digital_send_cmd() return failed.

## References
- https://git.kernel.org/stable/c/3f2960b39f22e26cf8addae93c3f5884d1c183c9
- https://git.kernel.org/stable/c/429054ec51e648d241a7e0b465cf44f6633334c5
- https://git.kernel.org/stable/c/564249219e5b5673a8416b5181875d828c3f1e8c
- https://git.kernel.org/stable/c/58e7dcc9ca29c14e44267a4d0ea61e3229124907
- https://git.kernel.org/stable/c/7ab488d7228a9dceb2456867f1f0919decf6efed
- https://git.kernel.org/stable/c/9881b0c860649f27ef2565deef011e516390f416
- https://git.kernel.org/stable/c/a67d47e32c91e2b10402cb8c081774cbf08edb2e
- https://git.kernel.org/stable/c/b7b023e6ff567e991c31cd425b0e1d16779c938b
