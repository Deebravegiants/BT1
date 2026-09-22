# [H] CVE-2021-47322

## Summary
Severity: High
Advisory: CVE-2021-47322
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47322
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4: Fix an Oops in pnfs_mark_request_commit() when doing O_DIRECT

Fix an Oopsable condition in pnfs_mark_request_commit() when we're
putting a set of writes on the commit list to reschedule them after a
failed pNFS attempt.

## References
- https://git.kernel.org/stable/c/7aec9f862411906f8c27071ba65a1e110ad7d2fd
- https://git.kernel.org/stable/c/7c96a2ee45be41d5a167e6332d202086752c36bb
- https://git.kernel.org/stable/c/3731d44bba8e0116b052b1b374476c5f6dd9a456
- https://git.kernel.org/stable/c/5c7ef8a3705542136a1e19b070e951f0730b2153
