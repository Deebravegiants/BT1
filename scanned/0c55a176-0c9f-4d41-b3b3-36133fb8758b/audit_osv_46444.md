# [H] CVE-2011-1070

## Summary
Severity: High
Advisory: CVE-2011-1070
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-14
Source: https://osv.dev/vulnerability/CVE-2011-1070
Type: osv

## Details
v86d before 0.1.10 do not verify if received netlink messages are sent by the kernel. This could allow unprivileged users to manipulate the video mode and potentially other consequences.

## References
- https://access.redhat.com/security/cve/cve-2011-1070
- https://seclists.org/oss-sec/2011/q1/315
- https://security-tracker.debian.org/tracker/CVE-2011-1070
- https://seclists.org/oss-sec/2011/q1/315
- https://access.redhat.com/security/cve/cve-2011-1070
