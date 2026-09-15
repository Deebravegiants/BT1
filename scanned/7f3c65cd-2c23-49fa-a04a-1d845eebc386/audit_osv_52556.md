# [M] CVE-2021-47577

## Summary
Severity: Medium
Advisory: CVE-2021-47577
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47577
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

io-wq: check for wq exit after adding new worker task_work

We check IO_WQ_BIT_EXIT before attempting to create a new worker, and
wq exit cancels pending work if we have any. But it's possible to have
a race between the two, where creation checks exit finding it not set,
but we're in the process of exiting. The exit side will cancel pending
creation task_work, but there's a gap where we add task_work after we've
canceled existing creations at exit time.

Fix this by checking the EXIT bit post adding the creation task_work.
If it's set, run the same cancelation that exit does.

## References
- https://git.kernel.org/stable/c/4b4e5bbf9386d4ec21d91c0cb0fd60b9bba778ec
- https://git.kernel.org/stable/c/71a85387546e50b1a37b0fa45dadcae3bfb35cf6
