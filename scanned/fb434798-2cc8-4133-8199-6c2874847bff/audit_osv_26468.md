# [M] scsi: storvsc: Fix handling of virtual Fibre Channel timeouts

## Summary
Severity: Medium
Advisory: CVE-2023-53245
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53245
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <4.14.323, >=4.15.0 <4.19.292, >=4.20.0 <5.4.254, >=5.5.0 <5.10.191, >=5.11.0 <5.15.127, >=5.16.0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: storvsc: Fix handling of virtual Fibre Channel timeouts

Hyper-V provides the ability to connect Fibre Channel LUNs to the host
system and present them in a guest VM as a SCSI device. I/O to the vFC
device is handled by the storvsc driver. The storvsc driver includes a
partial integration with the FC transport implemented in the generic
portion of the Linux SCSI subsystem so that FC attributes can be displayed
in /sys.  However, the partial integration means that some aspects of vFC
don't work properly. Unfortunately, a full and correct integration isn't
practical because of limitations in what Hyper-V provides to the guest.

In particular, in the context of Hyper-V storvsc, the FC transport timeout
function fc_eh_timed_out() causes a kernel panic because it can't find the
rport and dereferences a NULL pointer. The original patch that added the
call from storvsc_eh_timed_out() to fc_eh_timed_out() is faulty in this
regard.

In many cases a timeout is due to a transient condition, so the situation
can be improved by just continuing to wait like with other I/O requests
issued by storvsc, and avoiding the guaranteed panic. For a permanent
failure, continuing to wait may result in a hung thread instead of a panic,
which again may be better.

So fix the panic by removing the storvsc call to fc_eh_timed_out().  This
allows storvsc to keep waiting for a response.  The change has been tested
by users who experienced a panic in fc_eh_timed_out() due to transient
timeouts, and it solves their problem.

In the future we may want to deprecate the vFC functionality in storvsc
since it can't be fully fixed. But it has current users for whom it is
working well enough, so it should probably stay for a while longer.

## References
- https://git.kernel.org/stable/c/048ebc9a28fb918ee635dd4b2fcf4248eb6e4050
- https://git.kernel.org/stable/c/1678408d08f31a694d5150a56796dd04c9710b22
- https://git.kernel.org/stable/c/175544ad48cbf56affeef2a679c6a4d4fb1e2881
- https://git.kernel.org/stable/c/311db605e07f0d4fc0cc7ddb74f1e5692ea2f469
- https://git.kernel.org/stable/c/763c06565055ae373fe7f89c11e1447bd1ded264
- https://git.kernel.org/stable/c/7a792b3d888aab2c65389f9f4f9f2f6c000b1a0d
- https://git.kernel.org/stable/c/cd87f4df9865a53807001ed12c0f0420b14ececd
- https://git.kernel.org/stable/c/ed70fa5629a8b992a5372d7044d1db1f8fa6de29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53245.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53245
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
