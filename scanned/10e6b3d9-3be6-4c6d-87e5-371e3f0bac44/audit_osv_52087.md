# [M] CVE-2021-47056

## Summary
Severity: Medium
Advisory: CVE-2021-47056
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47056
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat - ADF_STATUS_PF_RUNNING should be set after adf_dev_init

ADF_STATUS_PF_RUNNING is (only) used and checked by adf_vf2pf_shutdown()
before calling adf_iov_putmsg()->mutex_lock(vf2pf_lock), however the
vf2pf_lock is initialized in adf_dev_init(), which can fail and when it
fail, the vf2pf_lock is either not initialized or destroyed, a subsequent
use of vf2pf_lock will cause issue.
To fix this issue, only set this flag if adf_dev_init() returns 0.

[    7.178404] BUG: KASAN: user-memory-access in __mutex_lock.isra.0+0x1ac/0x7c0
[    7.180345] Call Trace:
[    7.182576]  mutex_lock+0xc9/0xd0
[    7.183257]  adf_iov_putmsg+0x118/0x1a0 [intel_qat]
[    7.183541]  adf_vf2pf_shutdown+0x4d/0x7b [intel_qat]
[    7.183834]  adf_dev_shutdown+0x172/0x2b0 [intel_qat]
[    7.184127]  adf_probe+0x5e9/0x600 [qat_dh895xccvf]

## References
- https://git.kernel.org/stable/c/20fd40fc6f2c2b41dc6f637f88d494b14e9c21f1
- https://git.kernel.org/stable/c/446045cf682af12d9294765f6c46084b374b5654
- https://git.kernel.org/stable/c/8609f5cfdc872fc3a462efa6a3eca5cb1e2f6446
- https://git.kernel.org/stable/c/f4c4e07140687f42bfa40e091bb4a55d7960ce4d
- https://git.kernel.org/stable/c/05ec8192ee4bfdf2a8894a68350dac9f1a155fa6
- https://git.kernel.org/stable/c/09d16cee6285d37cc76311c29add6d97a7e4acda
- https://git.kernel.org/stable/c/1ea500ce6f7c9106e4a561d28e69215f3d451818
- https://git.kernel.org/stable/c/1f50392650ae794a1aea41c213c6a3e1c824413c
