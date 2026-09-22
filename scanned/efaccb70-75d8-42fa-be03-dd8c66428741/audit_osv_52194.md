# [M] CVE-2021-47183

## Summary
Severity: Medium
Advisory: CVE-2021-47183
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47183
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Fix link down processing to address NULL pointer dereference

If an FC link down transition while PLOGIs are outstanding to fabric well
known addresses, outstanding ABTS requests may result in a NULL pointer
dereference. Driver unload requests may hang with repeated "2878" log
messages.

The Link down processing results in ABTS requests for outstanding ELS
requests. The Abort WQEs are sent for the ELSs before the driver had set
the link state to down. Thus the driver is sending the Abort with the
expectation that an ABTS will be sent on the wire. The Abort request is
stalled waiting for the link to come up. In some conditions the driver may
auto-complete the ELSs thus if the link does come up, the Abort completions
may reference an invalid structure.

Fix by ensuring that Abort set the flag to avoid link traffic if issued due
to conditions where the link failed.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://git.kernel.org/stable/c/04c1af683270e4709a594bb1691b8800b945035a
- https://git.kernel.org/stable/c/1854f53ccd88ad4e7568ddfafafffe71f1ceb0a6
- https://git.kernel.org/stable/c/28de48a7cea495ab48082d9ff4ef63f7cb4e563a
