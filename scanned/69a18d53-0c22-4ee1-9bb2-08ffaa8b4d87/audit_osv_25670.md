# [C] CVE-2023-41360

## Summary
Severity: Critical
Advisory: CVE-2023-41360
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-08-29
Source: https://osv.dev/vulnerability/CVE-2023-41360
Type: osv

## Details
An issue was discovered in FRRouting FRR through 9.0. bgpd/bgp_packet.c can read the initial byte of the ORF header in an ahead-of-stream situation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41360.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JLG64IF3FU7V76K4TKCCXVNEE6P2VUDO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LMJNX44SMJM25JZO7XWHDQCOB4SNJPIE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WXR6PIVY4SWO7HDT4EY733H4X32SCPM4/
- https://nvd.nist.gov/vuln/detail/CVE-2023-41360
- https://github.com/FRRouting/frr/pull/14245
- https://lists.debian.org/debian-lts-announce/2023/09/msg00020.html
