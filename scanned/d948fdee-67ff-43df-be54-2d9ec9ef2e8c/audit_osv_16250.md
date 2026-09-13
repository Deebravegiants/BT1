# [H] CVE-2019-3827

## Summary
Severity: High
Advisory: CVE-2019-3827
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-3827
Type: osv

## Details
An incorrect permission check in the admin backend in gvfs before version 1.39.4 was found that allows reading and modify arbitrary files by privileged users without asking for password when no authentication agent is running. This vulnerability can be exploited by malicious programs running under privileges of users belonging to the wheel group to further escalate its privileges by modifying system files without user's knowledge. Successful exploitation requires uncommon system configuration.

## References
- https://access.redhat.com/errata/RHSA-2019:1517
- https://access.redhat.com/errata/RHSA-2019:2145
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3827
- https://gitlab.gnome.org/GNOME/gvfs/merge_requests/31
