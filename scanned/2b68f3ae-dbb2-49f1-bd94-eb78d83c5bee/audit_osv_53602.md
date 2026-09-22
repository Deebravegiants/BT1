# [M] CVE-2023-0468

## Summary
Severity: Medium
Advisory: CVE-2023-0468
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/CVE-2023-0468
Type: osv

## Details
A use-after-free flaw was found in io_uring/poll.c in io_poll_check_events in the io_uring subcomponent in the Linux Kernel due to a race condition of poll_refs. This flaw may cause a NULL pointer dereference.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2164024
