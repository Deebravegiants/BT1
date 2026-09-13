# [M] CVE-2019-9752

## Summary
Severity: Medium
Advisory: CVE-2019-9752
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-03-13
Source: https://osv.dev/vulnerability/CVE-2019-9752
Type: osv

## Details
An issue was discovered in Open Ticket Request System (OTRS) 5.x before 5.0.34, 6.x before 6.0.16, and 7.x before 7.0.4. An attacker who is logged into OTRS as an agent or a customer user may upload a carefully crafted resource in order to cause execution of JavaScript in the context of OTRS. This is related to Content-type mishandling in Kernel/Modules/PictureUpload.pm.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00066.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00077.html
- https://community.otrs.com/security-advisory-2019-01-security-update-for-otrs-framework
