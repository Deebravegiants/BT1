# [M] CVE-2021-47003

## Summary
Severity: Medium
Advisory: CVE-2021-47003
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47003
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: Fix potential null dereference on pointer status

There are calls to idxd_cmd_exec that pass a null status pointer however
a recent commit has added an assignment to *status that can end up
with a null pointer dereference.  The function expects a null status
pointer sometimes as there is a later assignment to *status where
status is first null checked.  Fix the issue by null checking status
before making the assignment.

Addresses-Coverity: ("Explicit null dereferenced")

## References
- https://git.kernel.org/stable/c/28ac8e03c43dfc6a703aa420d18222540b801120
- https://git.kernel.org/stable/c/5756f757c72501ef1a16f5f63f940623044180e9
- https://git.kernel.org/stable/c/7bc402f843e7817a4a808e7b9ab0bcd7ffd55bfa
- https://git.kernel.org/stable/c/2280b4cc29d8cdd2be3d1b2d1ea4f958e2131c97
