# [H] CVE-2021-47427

## Summary
Severity: High
Advisory: CVE-2021-47427
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47427
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: iscsi: Fix iscsi_task use after free

Commit d39df158518c ("scsi: iscsi: Have abort handler get ref to conn")
added iscsi_get_conn()/iscsi_put_conn() calls during abort handling but
then also changed the handling of the case where we detect an already
completed task where we now end up doing a goto to the common put/cleanup
code. This results in a iscsi_task use after free, because the common
cleanup code will do a put on the iscsi_task.

This reverts the goto and moves the iscsi_get_conn() to after we've checked
if the iscsi_task is valid.

## References
- https://git.kernel.org/stable/c/1642f51ac0d4f2b55d5748094c49ff8f7191b93c
- https://git.kernel.org/stable/c/258aad75c62146453d03028a44f2f1590d58e1f6
