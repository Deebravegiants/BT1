# [H] espintcp: Fix race condition in espintcp_close()

## Summary
Severity: High
Advisory: CVE-2026-23239
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-23239
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

espintcp: Fix race condition in espintcp_close()

This issue was discovered during a code audit.

After cancel_work_sync() is called from espintcp_close(),
espintcp_tx_work() can still be scheduled from paths such as
the Delayed ACK handler or ksoftirqd.
As a result, the espintcp_tx_work() worker may dereference a
freed espintcp ctx or sk.

The following is a simple race scenario:

           cpu0                             cpu1

  espintcp_close()
    cancel_work_sync(&ctx->work);
                                     espintcp_write_space()
                                       schedule_work(&ctx->work);

To prevent this race condition, cancel_work_sync() is
replaced with disable_work_sync().

## References
- https://git.kernel.org/stable/c/022ff7f347588de6e17879a1da6019647b21321b
- https://git.kernel.org/stable/c/664e9df53226b4505a0894817ecad2c610ab11d8
- https://git.kernel.org/stable/c/e1512c1db9e8794d8d130addd2615ec27231d994
- https://git.kernel.org/stable/c/f7ad8b1d0e421c524604d5076b73232093490d5c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23239.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
