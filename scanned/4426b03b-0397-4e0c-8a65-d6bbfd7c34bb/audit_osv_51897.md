# [H] CVE-2021-44733

## Summary
Severity: High
Advisory: CVE-2021-44733
Aliases: A-213173524, PUB-A-213173524
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-22
Source: https://osv.dev/vulnerability/CVE-2021-44733
Type: osv

## Details
A use-after-free exists in drivers/tee/tee_shm.c in the TEE subsystem in the Linux kernel through 5.15.11. This occurs because of a race condition in tee_shm_get_from_id during an attempt to free a shared memory object.

## References
- https://lore.kernel.org/lkml/20211215092501.1861229-1-jens.wiklander%40linaro.org/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dfd0743f1d9ea76931510ed150334d571fbab49d
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/drivers/tee/tee_shm.c
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://security.netapp.com/advisory/ntap-20220114-0003/
- https://www.debian.org/security/2022/dsa-5096
- https://github.com/pjlantz/optee-qemu/blob/main/README.md
