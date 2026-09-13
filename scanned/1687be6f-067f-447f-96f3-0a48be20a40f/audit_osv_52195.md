# [M] CVE-2021-47184

## Summary
Severity: Medium
Advisory: CVE-2021-47184
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47184
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: Fix NULL ptr dereference on VSI filter sync

Remove the reason of null pointer dereference in sync VSI filters.
Added new I40E_VSI_RELEASING flag to signalize deleting and releasing
of VSI resources to sync this thread with sync filters subtask.
Without this patch it is possible to start update the VSI filter list
after VSI is removed, that's causing a kernel oops.

## References
- https://git.kernel.org/stable/c/87c421ab4a43433cb009fea44bbbc77f46913e1d
- https://git.kernel.org/stable/c/c30162da91327e4cdf7cd03079f096bb3654738c
- https://git.kernel.org/stable/c/e91e8427a1e1633a0261e3bb0201c836ac5b3890
- https://git.kernel.org/stable/c/f866513ead4370402428ef724b03c3312295c178
- https://git.kernel.org/stable/c/37d9e304acd903a445df8208b8a13d707902dea6
- https://git.kernel.org/stable/c/78f2a9e831f9610e3655a0be5e675e1aa2472089
