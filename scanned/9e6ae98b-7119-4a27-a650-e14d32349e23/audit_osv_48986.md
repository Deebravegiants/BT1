# [H] CVE-2018-19655

## Summary
Severity: High
Advisory: CVE-2018-19655
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19655
Type: osv

## Details
A stack-based buffer overflow in the find_green() function of dcraw through 9.28, as used in ufraw-batch and many other products, may allow a remote attacker to cause a control-flow hijack, denial-of-service, or unspecified other impact via a maliciously crafted raw photo file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q3JX4A5F4DWP6NOEULXQXZ5AIH4GA62U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RD65NMWZ5OQNUIF7CLGKLDG4LVPPMJY7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XK4SHVVIZT6FHJVHOQSAFJMQWDLMWKDE/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=890086
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=906529
