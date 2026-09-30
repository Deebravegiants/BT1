# [M] CVE-2021-47398

## Summary
Severity: Medium
Advisory: CVE-2021-47398
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47398
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hfi1: Fix kernel pointer leak

Pointers should be printed with %p or %px rather than cast to 'unsigned
long long' and printed with %llx.  Change %llx to %p to print the secured
pointer.

## References
- https://git.kernel.org/stable/c/7d5cfafe8b4006a75b55c2f1fdfdb363f9a5cc98
- https://git.kernel.org/stable/c/714bfabe5f2901d96902e271d7217601fe4703e5
