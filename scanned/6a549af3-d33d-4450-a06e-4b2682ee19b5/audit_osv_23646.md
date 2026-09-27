# [H] tpm: fix reference counting for struct tpm_chip

## Summary
Severity: High
Advisory: CVE-2022-49287
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49287
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

tpm: fix reference counting for struct tpm_chip

The following sequence of operations results in a refcount warning:

1. Open device /dev/tpmrm.
2. Remove module tpm_tis_spi.
3. Write a TPM command to the file descriptor opened at step 1.

------------[ cut here ]------------
WARNING: CPU: 3 PID: 1161 at lib/refcount.c:25 kobject_get+0xa0/0xa4
refcount_t: addition on 0; use-after-free.
Modules linked in: tpm_tis_spi tpm_tis_core tpm mdio_bcm_unimac brcmfmac
sha256_generic libsha256 sha256_arm hci_uart btbcm bluetooth cfg80211 vc4
brcmutil ecdh_generic ecc snd_soc_core crc32_arm_ce libaes
raspberrypi_hwmon ac97_bus snd_pcm_dmaengine bcm2711_thermal snd_pcm
snd_timer genet snd phy_generic soundcore [last unloaded: spi_bcm2835]
CPU: 3 PID: 1161 Comm: hold_open Not tainted 5.10.0ls-main-dirty #2
Hardware name: BCM2711
[<c0410c3c>] (unwind_backtrace) from [<c040b580>] (show_stack+0x10/0x14)
[<c040b580>] (show_stack) from [<c1092174>] (dump_stack+0xc4/0xd8)
[<c1092174>] (dump_stack) from [<c0445a30>] (__warn+0x104/0x108)
[<c0445a30>] (__warn) from [<c0445aa8>] (warn_slowpath_fmt+0x74/0xb8)
[<c0445aa8>] (warn_slowpath_fmt) from [<c08435d0>] (kobject_get+0xa0/0xa4)
[<c08435d0>] (kobject_get) from [<bf0a715c>] (tpm_try_get_ops+0x14/0x54 [tpm])
[<bf0a715c>] (tpm_try_get_ops [tpm]) from [<bf0a7d6c>] (tpm_common_write+0x38/0x60 [tpm])
[<bf0a7d6c>] (tpm_common_write [tpm]) from [<c05a7ac0>] (vfs_write+0xc4/0x3c0)
[<c05a7ac0>] (vfs_write) from [<c05a7ee4>] (ksys_write+0x58/0xcc)
[<c05a7ee4>] (ksys_write) from [<c04001a0>] (ret_fast_syscall+0x0/0x4c)
Exception stack(0xc226bfa8 to 0xc226bff0)
bfa0:                   00000000 000105b4 00000003 beafe664 00000014 00000000
bfc0: 00000000 000105b4 000103f8 00000004 00000000 00000000 b6f9c000 beafe684
bfe0: 0000006c beafe648 0001056c b6eb6944
---[ end trace d4b8409def9b8b1f ]---

The reason for this warning is the attempt to get the chip->dev reference
in tpm_common_write() although the reference counter is already zero.

Since commit 8979b02aaf1d ("tpm: Fix reference count to main device") the
extra reference used to prevent a premature zero counter is never taken,
because the required TPM_CHIP_FLAG_TPM2 flag is never set.

Fix this by moving the TPM 2 character device handling from
tpm_chip_alloc() to tpm_add_char_device() which is called at a later point
in time when the flag has been set in case of TPM2.

Commit fdc915f7f719 ("tpm: expose spaces via a device link /dev/tpmrm<n>")
already introduced function tpm_devs_release() to release the extra
reference but did not implement the required put on chip->devs that results
in the call of this function.

Fix this by putting chip->devs in tpm_chip_unregister().

Finally move the new implementation for the TPM 2 handling into a new
function to avoid multiple checks for the TPM_CHIP_FLAG_TPM2 flag in the
good case and error cases.

## References
- https://git.kernel.org/stable/c/290e05f346d1829e849662c97e42d5ad984f5258
- https://git.kernel.org/stable/c/2f928c0d5c02dbab49e8c19d98725c822f6fc409
- https://git.kernel.org/stable/c/473a66f99cb8173c14138c5a5c69bfad04e8f9ac
- https://git.kernel.org/stable/c/662893b4f6bd466ff9e1cd454c44c26d32d554fe
- https://git.kernel.org/stable/c/6e7baf84149fb43950631415de231b3a41915aa3
- https://git.kernel.org/stable/c/7e0438f83dc769465ee663bb5dcf8cc154940712
- https://git.kernel.org/stable/c/a27ed2f3695baf15f9b34d2d7a1f9fc105539a81
- https://git.kernel.org/stable/c/cb64bd038beacb4331fe464a36c8b5481e8f51e2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49287.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
