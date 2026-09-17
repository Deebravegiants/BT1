# [H] CVE-2020-25712

## Summary
Severity: High
Advisory: CVE-2020-25712
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-25712
Type: osv

## Details
A flaw was found in xorg-x11-server before 1.20.10. A heap-buffer overflow in XkbSetDeviceInfo may lead to a privilege escalation vulnerability. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.x.org/archives/xorg-announce/2020-December/003066.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1887276
