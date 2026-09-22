# [M] CVE-2023-39193

## Summary
Severity: Medium
Advisory: CVE-2023-39193
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-10-09
Source: https://osv.dev/vulnerability/CVE-2023-39193
Type: osv

## Details
A flaw was found in the Netfilter subsystem in the Linux kernel. The sctp_mt_check did not validate the flag_count field. This flaw allows a local privileged (CAP_NET_ADMIN) attacker to trigger an out-of-bounds read, leading to a crash or information disclosure.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-39193
- https://access.redhat.com/errata/RHSA-2024:2394
- https://bugzilla.redhat.com/show_bug.cgi?id=2226787
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-18866/
