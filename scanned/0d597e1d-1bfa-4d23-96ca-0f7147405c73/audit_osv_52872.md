# [H] CVE-2022-1882

## Summary
Severity: High
Advisory: CVE-2022-1882
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-26
Source: https://osv.dev/vulnerability/CVE-2022-1882
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s pipes functionality in how a user performs manipulations with the pipe post_one_notification() after free_pipe_info() that is already called. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://lore.kernel.org/lkml/20220507115605.96775-1-tcs.kernel%40gmail.com/T/
- https://security.netapp.com/advisory/ntap-20220715-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2089701
