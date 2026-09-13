# [M] CVE-2020-36312

## Summary
Severity: Medium
Advisory: CVE-2020-36312
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2020-36312
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.8.10. virt/kvm/kvm_main.c has a kvm_io_bus_unregister_dev memory leak upon a kmalloc failure, aka CID-f65886606c2d.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.10
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f65886606c2d3b562716de030706dfe1bea4ed5e
