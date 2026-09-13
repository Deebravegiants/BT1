# [M] CVE-2021-3468

## Summary
Severity: Medium
Advisory: CVE-2021-3468
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-3468
Type: osv

## Details
A flaw was found in avahi in versions 0.6 up to 0.8. The event used to signal the termination of the client connection on the avahi Unix socket is not correctly handled in the client_work function, allowing a local attacker to trigger an infinite loop. The highest threat from this vulnerability is to the availability of the avahi service, which becomes unresponsive after this flaw is triggered.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00028.html
- https://lists.debian.org/debian-lts-announce/2022/06/msg00009.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1939614
