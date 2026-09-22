# [M] CVE-2017-10972

## Summary
Severity: Medium
Advisory: CVE-2017-10972
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-06
Source: https://osv.dev/vulnerability/CVE-2017-10972
Type: osv

## Details
Uninitialized data in endianness conversion in the XEvent handling of the X.Org X Server before 2017-06-19 allowed authenticated malicious users to access potentially privileged data from the X server.

## References
- http://www.debian.org/security/2017/dsa-3905
- http://www.securityfocus.com/bid/99543
- https://bugzilla.suse.com/show_bug.cgi?id=1035283
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=05442de962d3dc624f79fc1a00eca3ffc5489ced
