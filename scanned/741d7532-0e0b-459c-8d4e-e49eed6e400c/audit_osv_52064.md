# [H] CVE-2021-47026

## Summary
Severity: High
Advisory: CVE-2021-47026
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47026
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rtrs-clt: destroy sysfs after removing session from active list

A session can be removed dynamically by sysfs interface "remove_path" that
eventually calls rtrs_clt_remove_path_from_sysfs function.  The current
rtrs_clt_remove_path_from_sysfs first removes the sysfs interfaces and
frees sess->stats object. Second it removes the session from the active
list.

Therefore some functions could access non-connected session and access the
freed sess->stats object even-if they check the session status before
accessing the session.

For instance rtrs_clt_request and get_next_path_min_inflight check the
session status and try to send IO to the session.  The session status
could be changed when they are trying to send IO but they could not catch
the change and update the statistics information in sess->stats object,
and generate use-after-free problem.
(see: "RDMA/rtrs-clt: Check state of the rtrs_clt_sess before reading its
stats")

This patch changes the rtrs_clt_remove_path_from_sysfs to remove the
session from the active session list and then destroy the sysfs
interfaces.

Each function still should check the session status because closing or
error recovery paths can change the status.

## References
- https://git.kernel.org/stable/c/676171f9405dcaa45a33d18241c32f387dbaae39
- https://git.kernel.org/stable/c/7f4a8592ff29f19c5a2ca549d0973821319afaad
- https://git.kernel.org/stable/c/b64415c6b3476cf9fa4d0aea3807065b8403a937
- https://git.kernel.org/stable/c/d3cca8067d43dfee4a3535c645b55f618708dccb
