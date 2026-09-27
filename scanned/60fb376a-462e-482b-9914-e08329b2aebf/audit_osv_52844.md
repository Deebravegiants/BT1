# [H] CVE-2022-1786

## Summary
Severity: High
Advisory: CVE-2022-1786
Aliases: A-230867044, A-233078742, ASB-A-230867044, ASB-A-233078742
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2022-1786
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s io_uring subsystem in the way a user sets up a ring with IORING_SETUP_IOPOLL with more than one task completing submissions on this ring. This flaw allows a local user to crash or escalate their privileges on the system.

## References
- https://security.netapp.com/advisory/ntap-20220722-0001/
- https://www.debian.org/security/2022/dsa-5161
- https://bugzilla.redhat.com/show_bug.cgi?id=2087760
