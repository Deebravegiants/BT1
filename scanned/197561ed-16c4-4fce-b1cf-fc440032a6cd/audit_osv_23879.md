# [M] pinctrl: ralink: Check for null return of devm_kcalloc

## Summary
Severity: Medium
Advisory: CVE-2022-49608
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49608
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: ralink: Check for null return of devm_kcalloc

Because of the possible failure of the allocation, data->domains might
be NULL pointer and will cause the dereference of the NULL pointer
later.
Therefore, it might be better to check it and directly return -ENOMEM
without releasing data manually if fails, because the comment of the
devm_kmalloc() says "Memory allocated with this function is
automatically freed on driver detach.".

## References
- https://git.kernel.org/stable/c/13596e6c9e541e90e5fc2c52b23f08b951370da9
- https://git.kernel.org/stable/c/44016a85419ca0d4f1e4d0127b330f8e4e2a57d0
- https://git.kernel.org/stable/c/5595d30c4dc27d939635c3188c68203b6ece1711
- https://git.kernel.org/stable/c/5694b162f275fb9a9f89422701b2b963be11e496
- https://git.kernel.org/stable/c/6194c021496addc11763d1ffa89ce5751889fe3c
- https://git.kernel.org/stable/c/c3b821e8e406d5650e587b7ac624ac24e9b780a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49608.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49608
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
