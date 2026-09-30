# [H] CVE-2022-3238

## Summary
Severity: High
Advisory: CVE-2022-3238
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-14
Source: https://osv.dev/vulnerability/CVE-2022-3238
Type: osv

## Details
A double-free flaw was found in the Linux kernel’s NTFS3 subsystem in how a user triggers remount and umount simultaneously. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2127927
