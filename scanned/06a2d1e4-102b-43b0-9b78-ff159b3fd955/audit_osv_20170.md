# [C] CVE-2021-3185

## Summary
Severity: Critical
Advisory: CVE-2021-3185
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2021-3185
Type: osv

## Details
A flaw was found in the gstreamer h264 component of gst-plugins-bad before v1.18.1 where when parsing a h264 header, an attacker could cause the stack to be smashed, memory corruption and possibly code execution.

## References
- https://security.gentoo.org/glsa/202208-31
- https://bugzilla.redhat.com/show_bug.cgi?id=1917192
