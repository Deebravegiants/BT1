# [M] CVE-2021-47389

## Summary
Severity: Medium
Advisory: CVE-2021-47389
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47389
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SVM: fix missing sev_decommission in sev_receive_start

DECOMMISSION the current SEV context if binding an ASID fails after
RECEIVE_START.  Per AMD's SEV API, RECEIVE_START generates a new guest
context and thus needs to be paired with DECOMMISSION:

     The RECEIVE_START command is the only command other than the LAUNCH_START
     command that generates a new guest context and guest handle.

The missing DECOMMISSION can result in subsequent SEV launch failures,
as the firmware leaks memory and might not able to allocate more SEV
guest contexts in the future.

Note, LAUNCH_START suffered the same bug, but was previously fixed by
commit 934002cd660b ("KVM: SVM: Call SEV Guest Decommission if ASID
binding fails").

## References
- https://git.kernel.org/stable/c/efd7866e114dcb44f86d151e843f8276b7efbc67
- https://git.kernel.org/stable/c/f1815e0aa770f2127c5df31eb5c2f0e37b60fa77
