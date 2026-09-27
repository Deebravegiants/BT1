# [H] CVE-2022-1973

## Summary
Severity: High
Advisory: CVE-2022-1973
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-08-05
Source: https://osv.dev/vulnerability/CVE-2022-1973
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel in log_replay in fs/ntfs3/fslog.c in the NTFS journal. This flaw allows a local attacker to crash the system and leads to a kernel information leak problem.

## References
- https://security.netapp.com/advisory/ntap-20230120-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2092542
