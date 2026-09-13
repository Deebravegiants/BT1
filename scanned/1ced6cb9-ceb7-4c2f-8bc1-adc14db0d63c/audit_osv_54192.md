# [M] CVE-2023-42755

## Summary
Severity: Medium
Advisory: CVE-2023-42755
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-05
Source: https://osv.dev/vulnerability/CVE-2023-42755
Type: osv

## Details
A flaw was found in the IPv4 Resource Reservation Protocol (RSVP) classifier in the Linux kernel. The xprt pointer may go beyond the linear part of the skb, leading to an out-of-bounds read in the `rsvp_classify` function. This issue may allow a local user to crash the system and cause a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-42755
- https://bugzilla.redhat.com/show_bug.cgi?id=2239847
- https://seclists.org/oss-sec/2023/q3/229
