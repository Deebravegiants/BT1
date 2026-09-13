# [H] CVE-2020-25708

## Summary
Severity: High
Advisory: CVE-2020-25708
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-27
Source: https://osv.dev/vulnerability/CVE-2020-25708
Type: osv

## Details
A divide by zero issue was found to occur in libvncserver-0.9.12. A malicious client could use this flaw to send a specially crafted message that, when processed by the VNC server, would lead to a floating point exception, resulting in a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00035.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1896739
