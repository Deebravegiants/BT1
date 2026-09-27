# [H] net/smc: reject CHID-0 ACCEPT that matches an empty ism_dev slot

## Summary
Severity: High
Advisory: CVE-2026-64048
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64048
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: reject CHID-0 ACCEPT that matches an empty ism_dev slot

On the SMC-D client, slot 0 of ini->ism_dev[]/ini->ism_chid[] is
reserved for an SMC-Dv1 device. smc_find_ism_v2_device_clnt()
populates V2 entries starting at index 1, so when no V1 device is
selected slot 0 is left in its kzalloc()'ed state with ism_dev[0] ==
NULL and ism_chid[0] == 0.

smc_v2_determine_accepted_chid() then matches the peer's CHID against
the array starting from index 0 using the CHID alone. A malicious
peer replying to a SMC-Dv2-only proposal with d1.chid == 0 matches
the empty slot, ini->ism_selected becomes 0, and the subsequent
ism_dev[0]->lgr_lock dereference in smc_conn_create() faults at
offsetof(struct smcd_dev, lgr_lock) == 0x68:

  BUG: KASAN: null-ptr-deref in _raw_spin_lock_bh+0x79/0xe0
  Write of size 4 at addr 0000000000000068 by task exploit/144
  Call Trace:
   _raw_spin_lock_bh
   smc_conn_create (net/smc/smc_core.c:1997)
   __smc_connect (net/smc/af_smc.c:1447)
   smc_connect (net/smc/af_smc.c:1720)
   __sys_connect
   __x64_sys_connect
   do_syscall_64

Require ism_dev[i] to be non-NULL before accepting a CHID match.

## References
- https://git.kernel.org/stable/c/277740023def559a4a2ddc3e8e784ee37a0f16a9
- https://git.kernel.org/stable/c/53eb7bd09aace72fa17510d80e0caf5ca058c231
- https://git.kernel.org/stable/c/65edb3b0822cfe5041be8fbabebd57e2e5ad9f4e
- https://git.kernel.org/stable/c/6927cacf2b10d4fa80c1a2d407512ef9397c59c6
- https://git.kernel.org/stable/c/903f7688ffeb9b323d70652c01f554bd4ba2a3d6
- https://git.kernel.org/stable/c/afa9036b8c9963947b487c36e332df6a42c96fcb
- https://git.kernel.org/stable/c/d38ba387244e5c5f7db3e11ea98bc2c7beccb0c0
- https://git.kernel.org/stable/c/dd2f9dd83c68abd7ba7ded7075290b016cb7ecd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64048.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64048
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
