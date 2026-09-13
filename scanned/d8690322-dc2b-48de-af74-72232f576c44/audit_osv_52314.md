# [M] CVE-2021-47319

## Summary
Severity: Medium
Advisory: CVE-2021-47319
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47319
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-blk: Fix memory leak among suspend/resume procedure

The vblk->vqs should be freed before we call init_vqs()
in virtblk_restore().

## References
- https://git.kernel.org/stable/c/b71ba22e7c6c6b279c66f53ee7818709774efa1f
- https://git.kernel.org/stable/c/cd24da0db9f75ca11eaf6060f0ccb90e2f3be3b0
- https://git.kernel.org/stable/c/ca2b8ae93a6da9839dc7f9eb9199b18aa03c3dae
- https://git.kernel.org/stable/c/04c6e60b884cb5e94ff32af46867fb41d5848358
- https://git.kernel.org/stable/c/102d6bc6475ab09bab579c18704e6cf8d898e93c
- https://git.kernel.org/stable/c/29a2f4a3214aa14d61cc9737c9f886dae9dbb710
- https://git.kernel.org/stable/c/381bde79d11e596002edfd914e6714291826967a
- https://git.kernel.org/stable/c/600942d2fd49b90e44857d20c774b20d16f3130f
- https://git.kernel.org/stable/c/863da837964c80c72e368a4f748c30d25daa1815
