# [M] CVE-2018-14543

## Summary
Severity: Medium
Advisory: CVE-2018-14543
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-14543
Type: osv

## Details
There exists one NULL pointer dereference vulnerability in AP4_JsonInspector::AddField in Ap4Atom.cpp in Bento4 1.5.1-624, which can allow attackers to cause a denial-of-service via a crafted mp4 file. This vulnerability can be triggered by the executable mp4dump.

## References
- https://github.com/axiomatic-systems/Bento4/issues/292
