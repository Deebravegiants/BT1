# [C] nvme: fix a possible use-after-free in controller reset during load

## Summary
Severity: Critical
Advisory: CVE-2022-48790
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48790
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.231, >=4.20.0 <5.4.181, >=5.5.0 <5.10.102, >=5.11.0 <5.15.25, >=5.16.0 <5.16.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme: fix a possible use-after-free in controller reset during load

Unlike .queue_rq, in .submit_async_event drivers may not check the ctrl
readiness for AER submission. This may lead to a use-after-free
condition that was observed with nvme-tcp.

The race condition may happen in the following scenario:
1. driver executes its reset_ctrl_work
2. -> nvme_stop_ctrl - flushes ctrl async_event_work
3. ctrl sends AEN which is received by the host, which in turn
   schedules AEN handling
4. teardown admin queue (which releases the queue socket)
5. AEN processed, submits another AER, calling the driver to submit
6. driver attempts to send the cmd
==> use-after-free

In order to fix that, add ctrl state check to validate the ctrl
is actually able to accept the AER submission.

This addresses the above race in controller resets because the driver
during teardown should:
1. change ctrl state to RESETTING
2. flush async_event_work (as well as other async work elements)

So after 1,2, any other AER command will find the
ctrl state to be RESETTING and bail out without submitting the AER.

## References
- https://git.kernel.org/stable/c/0ead57ceb21bbf15963b4874c2ac67143455382f
- https://git.kernel.org/stable/c/0fa0f99fc84e41057cbdd2efbfe91c6b2f47dd9d
- https://git.kernel.org/stable/c/70356b756a58704e5c8818cb09da5854af87e765
- https://git.kernel.org/stable/c/9e956a2596ae276124ef0d96829c013dd0faf861
- https://git.kernel.org/stable/c/a25e460fbb0340488d119fb2e28fe3f829b7417e
- https://git.kernel.org/stable/c/e043fb5a0336ee74614e26f0d9f36f1f5bb6d606
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48790.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48790
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
