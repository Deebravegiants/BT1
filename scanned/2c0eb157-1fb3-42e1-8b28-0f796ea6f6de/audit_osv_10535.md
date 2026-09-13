# [M] CVE-2017-16883

## Summary
Severity: Medium
Advisory: CVE-2017-16883
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-18
Source: https://osv.dev/vulnerability/CVE-2017-16883
Type: osv

## Details
The outputSWF_TEXT_RECORD function in util/outputscript.c in libming <= 0.4.8 is vulnerable to a NULL pointer dereference, which may allow attackers to cause a denial of service via a crafted swf file.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00014.html
- https://github.com/libming/libming/issues/77
