# [H] CVE-2020-25866

## Summary
Severity: High
Advisory: CVE-2020-25866
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-25866
Type: osv

## Details
In Wireshark 3.2.0 to 3.2.6 and 3.0.0 to 3.0.13, the BLIP protocol dissector has a NULL pointer dereference because a buffer was sized for compressed (not uncompressed) messages. This was addressed in epan/dissectors/packet-blip.c by allowing reasonable compression ratios and rejecting ZIP bombs.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4DQHPKZFQ7W3X34RYN3FWFYCFJD4FXJW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6IGRYKW4XLR44YDWTAH547ODYYBYPB2D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZUHMK5HYTUUDXA64T2TAMAFMYV674QBW/
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00038.html
- https://www.wireshark.org/security/wnpa-sec-2020-13.html
- https://gitlab.com/wireshark/wireshark/-/issues/16866
- https://gitlab.com/wireshark/wireshark/-/commit/4a948427100b6c109f4ec7b4361f0d2aec5e5c3f
- https://www.oracle.com/security-alerts/cpujan2021.html
