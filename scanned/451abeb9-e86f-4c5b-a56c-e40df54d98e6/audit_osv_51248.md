# [H] CVE-2021-22600

## Summary
Severity: High
Advisory: CVE-2021-22600
Aliases: A-213464034, ASB-A-213464034, PUB-A-213464034
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-26
Source: https://osv.dev/vulnerability/CVE-2021-22600
Type: osv

## Details
A double free bug in packet_set_ring() in net/packet/af_packet.c can be exploited by a local user through crafted syscalls to escalate privileges or deny service. We recommend upgrading kernel past the effected versions or rebuilding past ec6af094ea28f0f2dda1a6a33b14cd57e36a9755

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-22600
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://security.netapp.com/advisory/ntap-20230110-0002/
- https://www.debian.org/security/2022/dsa-5096
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=ec6af094ea28f0f2dda1a6a33b14cd57e36a9755
