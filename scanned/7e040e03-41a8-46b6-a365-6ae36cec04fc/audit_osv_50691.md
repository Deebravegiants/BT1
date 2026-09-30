# [C] CVE-2020-28926

## Summary
Severity: Critical
Advisory: CVE-2020-28926
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-30
Source: https://osv.dev/vulnerability/CVE-2020-28926
Type: osv

## Details
ReadyMedia (aka MiniDLNA) before versions 1.3.0 allows remote code execution. Sending a malicious UPnP HTTP request to the miniDLNA service using HTTP chunked encoding can lead to a signedness bug resulting in a buffer overflow in calls to memcpy/memmove.

## References
- https://sourceforge.net/projects/minidlna/
- https://www.debian.org/security/2020/dsa-4806
- https://lists.debian.org/debian-lts-announce/2020/12/msg00017.html
- https://www.rootshellsecurity.net/remote-heap-corruption-bug-discovery-minidlna/
