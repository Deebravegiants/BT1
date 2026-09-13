# [H] scsi: qla2xxx: Implement ref count for SRB

## Summary
Severity: High
Advisory: CVE-2022-49159
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49159
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Implement ref count for SRB

The timeout handler and the done function are racing. When
qla2x00_async_iocb_timeout() starts to run it can be preempted by the
normal response path (via the firmware?). qla24xx_async_gpsc_sp_done()
releases the SRB unconditionally. When scheduling back to
qla2x00_async_iocb_timeout() qla24xx_async_abort_cmd() will access an freed
sp->qpair pointer:

  qla2xxx [0000:83:00.0]-2871:0: Async-gpsc timeout - hdl=63d portid=234500 50:06:0e:80:08:77:b6:21.
  qla2xxx [0000:83:00.0]-2853:0: Async done-gpsc res 0, WWPN 50:06:0e:80:08:77:b6:21
  qla2xxx [0000:83:00.0]-2854:0: Async-gpsc OUT WWPN 20:45:00:27:f8:75:33:00 speeds=2c00 speed=0400.
  qla2xxx [0000:83:00.0]-28d8:0: qla24xx_handle_gpsc_event 50:06:0e:80:08:77:b6:21 DS 7 LS 6 rc 0 login 1|1 rscn 1|0 lid 5
  BUG: unable to handle kernel NULL pointer dereference at 0000000000000004
  IP: qla24xx_async_abort_cmd+0x1b/0x1c0 [qla2xxx]

Obvious solution to this is to introduce a reference counter. One reference
is taken for the normal code path (the 'good' case) and one for the timeout
path. As we always race between the normal good case and the timeout/abort
handler we need to serialize it. Also we cannot assume any order between
the handlers. Since this is slow path we can use proper synchronization via
locks.

When we are able to cancel a timer (del_timer returns 1) we know there
can't be any error handling in progress because the timeout handler hasn't
expired yet, thus we can safely decrement the refcounter by one.

If we are not able to cancel the timer, we know an abort handler is
running. We have to make sure we call sp->done() in the abort handlers
before calling kref_put().

## References
- https://git.kernel.org/stable/c/31e6cdbe0eae37badceb5e0d4f06cf051432fd77
- https://git.kernel.org/stable/c/ceda7f794f3dfe272491e93e3e93049f8be5f07b
- https://git.kernel.org/stable/c/e140723f78ff418c8df7d990e102e07b65c87d4a
- https://git.kernel.org/stable/c/e17111dd2fda81c35f309b1e5b6ab35809a375e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49159.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49159
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
