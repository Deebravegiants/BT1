# [H] nghttp2 Denial of service: Assertion failure due to the missing state validation

## Summary
Severity: High
Advisory: CVE-2026-27135
Aliases: GHSA-6933-cjhr-5qg6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-27135
Type: osv

## Details
nghttp2 is an implementation of the Hypertext Transfer Protocol version 2 in C. Prior to version 1.68.1, the nghttp2 library stops reading the incoming data when user facing public API `nghttp2_session_terminate_session` or `nghttp2_session_terminate_session2` is called by the application. They might be called internally by the library when it detects the situation that is subject to connection error. Due to the missing internal state validation, the library keeps reading the rest of the data after one of those APIs is called. Then receiving a malformed frame that causes FRAME_SIZE_ERROR causes assertion failure. nghttp2 v1.68.1 adds missing state validation to avoid assertion failure. No known workarounds are available.

## References
- http://www.openwall.com/lists/oss-security/2026/03/20/3
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://lists.debian.org/debian-lts-announce/2026/05/msg00025.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27135.json
- https://access.redhat.com/errata/RHSA-2026:10065
- https://access.redhat.com/errata/RHSA-2026:11768
- https://access.redhat.com/errata/RHSA-2026:13812
- https://access.redhat.com/errata/RHSA-2026:14773
- https://access.redhat.com/errata/RHSA-2026:14937
- https://access.redhat.com/errata/RHSA-2026:15087
- https://access.redhat.com/errata/RHSA-2026:16008
- https://access.redhat.com/errata/RHSA-2026:16009
- https://access.redhat.com/errata/RHSA-2026:16030
- https://access.redhat.com/errata/RHSA-2026:16174
- https://access.redhat.com/errata/RHSA-2026:17596
- https://access.redhat.com/errata/RHSA-2026:19724
- https://access.redhat.com/errata/RHSA-2026:19725
- https://access.redhat.com/errata/RHSA-2026:20040
- https://access.redhat.com/errata/RHSA-2026:20087
- https://access.redhat.com/errata/RHSA-2026:21656
