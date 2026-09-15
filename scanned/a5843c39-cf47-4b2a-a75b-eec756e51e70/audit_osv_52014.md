# [M] CVE-2021-46963

## Summary
Severity: Medium
Advisory: CVE-2021-46963
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46963
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix crash in qla2xxx_mqueuecommand()

    RIP: 0010:kmem_cache_free+0xfa/0x1b0
    Call Trace:
       qla2xxx_mqueuecommand+0x2b5/0x2c0 [qla2xxx]
       scsi_queue_rq+0x5e2/0xa40
       __blk_mq_try_issue_directly+0x128/0x1d0
       blk_mq_request_issue_directly+0x4e/0xb0

Fix incorrect call to free srb in qla2xxx_mqueuecommand(), as srb is now
allocated by upper layers. This fixes smatch warning of srb unintended
free.

## References
- https://git.kernel.org/stable/c/6641df81ab799f28a5d564f860233dd26cca0d93
- https://git.kernel.org/stable/c/702cdaa2c6283c135ef16d52e0e4e3c1005aa538
- https://git.kernel.org/stable/c/77509a238547863040a42d57c72403f7d4c89a8f
- https://git.kernel.org/stable/c/80ef24175df2cba3860d0369d1c662b49ee2de56
- https://git.kernel.org/stable/c/a73208e3244127ef9f2cdf24e4adb947aaa32053
- https://git.kernel.org/stable/c/c5ab9b67d8b061de74e2ca51bf787ee599bd7f89
