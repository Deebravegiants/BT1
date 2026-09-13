# [H] CVE-2018-15688

## Summary
Severity: High
Advisory: CVE-2018-15688
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-26
Source: https://osv.dev/vulnerability/CVE-2018-15688
Type: osv

## Details
A buffer overflow vulnerability in the dhcp6 client of systemd allows a malicious dhcp6 server to overwrite heap memory in systemd-networkd. Affected releases are systemd: versions up to and including 239.

## References
- http://www.securityfocus.com/bid/105745
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3665
- https://access.redhat.com/errata/RHSA-2019:0049
- https://lists.debian.org/debian-lts-announce/2018/11/msg00017.html
- https://security.gentoo.org/glsa/201810-10
- https://usn.ubuntu.com/3806-1/
- https://usn.ubuntu.com/3807-1/
- https://github.com/systemd/systemd/pull/10518
