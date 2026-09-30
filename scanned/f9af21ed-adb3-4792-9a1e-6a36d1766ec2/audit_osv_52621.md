# [M] CVE-2021-47651

## Summary
Severity: Medium
Advisory: CVE-2021-47651
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47651
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: qcom: rpmpd: Check for null return of devm_kcalloc

Because of the possible failure of the allocation, data->domains might
be NULL pointer and will cause the dereference of the NULL pointer
later.
Therefore, it might be better to check it and directly return -ENOMEM
without releasing data manually if fails, because the comment of the
devm_kmalloc() says "Memory allocated with this function is
automatically freed on driver detach.".

## References
- https://git.kernel.org/stable/c/5a811126d38f9767a20cc271b34db7c8efc5a46c
- https://git.kernel.org/stable/c/724376c30af5a57686b223dbcd6188e07d2a1de2
- https://git.kernel.org/stable/c/755dbc3d73789ac9f0017c729abf5e4b153bf799
- https://git.kernel.org/stable/c/84b89fa877ad576e9ee8130f412cfd592f274508
- https://git.kernel.org/stable/c/b5d6eba71997b6d661935d2b15094ac7f9f6132d
- https://git.kernel.org/stable/c/31b5124d742969ea8bf7a1360596f548ca23e770
