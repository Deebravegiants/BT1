# [H] CVE-2017-9986

## Summary
Severity: High
Advisory: CVE-2017-9986
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9986
Type: osv

## Details
The intr function in sound/oss/msnd_pinnacle.c in the Linux kernel through 4.11.7 allows local users to cause a denial of service (over-boundary access) or possibly have unspecified other impact by changing the value of a message queue head pointer between two kernel reads of that value, aka a "double fetch" vulnerability.

## References
- http://www.securityfocus.com/bid/99336
- https://bugzilla.kernel.org/show_bug.cgi?id=196135
