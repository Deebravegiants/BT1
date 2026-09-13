# [M] CVE-2023-39194

## Summary
Severity: Medium
Advisory: CVE-2023-39194
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-09
Source: https://osv.dev/vulnerability/CVE-2023-39194
Type: osv

## Details
A flaw was found in the XFRM subsystem in the Linux kernel. The specific flaw exists within the processing of state filters, which can result in a read past the end of an allocated buffer. This flaw allows a local privileged (CAP_NET_ADMIN) attacker to trigger an out-of-bounds read, potentially leading to an information disclosure.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-39194
- https://access.redhat.com/errata/RHSA-2024:2394
- https://access.redhat.com/errata/RHSA-2024:2950
- https://bugzilla.redhat.com/show_bug.cgi?id=2226788
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-18111/
