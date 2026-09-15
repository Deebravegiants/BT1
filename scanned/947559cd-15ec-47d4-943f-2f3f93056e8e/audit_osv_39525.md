# [H] media: amphion: Fix race between m2m job_abort and device_run

## Summary
Severity: High
Advisory: CVE-2026-46058
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46058
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: amphion: Fix race between m2m job_abort and device_run

Fix kernel panic caused by race condition where v4l2_m2m_ctx_release()
frees m2m_ctx while v4l2_m2m_try_run() is about to call device_run
with the same context.

Race sequence:
  v4l2_m2m_try_run():           v4l2_m2m_ctx_release():
    lock/unlock                   v4l2_m2m_cancel_job()
                                    job_abort()
                                      v4l2_m2m_job_finish()
                                  kfree(m2m_ctx)  <- frees ctx
    device_run()  <- use-after-free crash at 0x538

Crash trace:
  Unable to handle kernel read from unreadable memory at virtual address
  0000000000000538
  v4l2_m2m_try_run+0x78/0x138
  v4l2_m2m_device_run_work+0x14/0x20

The amphion vpu driver does not rely on the m2m framework's device_run
callback to perform encode/decode operations.

Fix the race by preventing m2m framework job scheduling entirely:
- Add job_ready callback returning 0 (no jobs ready for m2m framework)
- Remove job_abort callback to avoid the race condition

## References
- https://git.kernel.org/stable/c/42dc622776f3ce1a6c31b13bdc686f7295e3b323
- https://git.kernel.org/stable/c/516467052fdfc6a13eadc70d43420ae57436bf3c
- https://git.kernel.org/stable/c/6be2cb75bc1300080cfc8051579f22efae9401f7
- https://git.kernel.org/stable/c/8cd35ceadcfc8c5da2eb7f7ce24525ce9d4ee62e
- https://git.kernel.org/stable/c/da4f46c5cf1d26e6b09418ad453e152f2e75a02c
- https://git.kernel.org/stable/c/fdc150dac1adb9a98be9d6956cff0348838b024a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46058.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46058
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
