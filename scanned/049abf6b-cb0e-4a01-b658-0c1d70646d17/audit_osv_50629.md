# [M] CVE-2020-26088

## Summary
Severity: Medium
Advisory: CVE-2020-26088
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-09-24
Source: https://osv.dev/vulnerability/CVE-2020-26088
Type: osv

## Details
A missing CAP_NET_RAW check in NFC socket creation in net/nfc/rawsock.c in the Linux kernel before 5.8.2 could be used by local attackers to create raw sockets, bypassing security mechanisms, aka CID-26896f01467a.

## References
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- https://github.com/torvalds/linux/commit/26896f01467a28651f7a536143fe5ac8449d4041
- https://usn.ubuntu.com/4578-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.2
