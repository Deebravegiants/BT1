# [H] sched/mmcid: Don't assume CID is CPU owned on mode switch

## Summary
Severity: High
Advisory: CVE-2026-23225
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-23225
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched/mmcid: Don't assume CID is CPU owned on mode switch

Shinichiro reported a KASAN UAF, which is actually an out of bounds access
in the MMCID management code.

   CPU0						CPU1
   						T1 runs in userspace
   T0: fork(T4) -> Switch to per CPU CID mode
         fixup() set MM_CID_TRANSIT on T1/CPU1
   T4 exit()
   T3 exit()
   T2 exit()
						T1 exit() switch to per task mode
						 ---> Out of bounds access.

As T1 has not scheduled after T0 set the TRANSIT bit, it exits with the
TRANSIT bit set. sched_mm_cid_remove_user() clears the TRANSIT bit in
the task and drops the CID, but it does not touch the per CPU storage.
That's functionally correct because a CID is only owned by the CPU when
the ONCPU bit is set, which is mutually exclusive with the TRANSIT flag.

Now sched_mm_cid_exit() assumes that the CID is CPU owned because the
prior mode was per CPU. It invokes mm_drop_cid_on_cpu() which clears the
not set ONCPU bit and then invokes clear_bit() with an insanely large
bit number because TRANSIT is set (bit 29).

Prevent that by actually validating that the CID is CPU owned in
mm_drop_cid_on_cpu().

## References
- https://git.kernel.org/stable/c/1e83ccd5921a610ef409a7d4e56db27822b4ea39
- https://git.kernel.org/stable/c/81f29975631db8a78651b3140ecd0f88ffafc476
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23225.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23225
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
