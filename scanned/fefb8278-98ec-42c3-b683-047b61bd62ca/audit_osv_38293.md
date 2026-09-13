# [H] CVE-2026-37457

## Summary
Severity: High
Advisory: CVE-2026-37457
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-37457
Type: osv

## Details
An off-by-one out-of-bounds write vulnerability in the bgp_flowspec_op_decode() function (bgpd/bgp_flowspec_util.c) of FRRouting (FRR) stable/10.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted FlowSpec component.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-37457.json
- https://access.redhat.com/errata/RHSA-2026:24340
- https://access.redhat.com/errata/RHSA-2026:24347
- https://access.redhat.com/errata/RHSA-2026:24370
- https://access.redhat.com/errata/RHSA-2026:24371
- https://access.redhat.com/security/cve/CVE-2026-37457
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37457.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-37457
- https://bugzilla.redhat.com/show_bug.cgi?id=2464548
- https://github.com/FRRouting/frr/commit/0e6882bc72c0278988a47b2f0f73b7a91099a25c
