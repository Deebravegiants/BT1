# [M] CVE-2019-9516

## Summary
Severity: Medium
Advisory: CVE-2019-9516
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/CVE-2019-9516
Type: osv

## Details
Some HTTP/2 implementations are vulnerable to a header leak, potentially leading to a denial of service. The attacker sends a stream of headers with a 0-length header name and 0-length header value, optionally Huffman encoded into 1-byte or greater headers. Some implementations allocate memory for these headers and keep the allocation alive until the session dies. This can consume excess memory.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ZQGHE3WTYLYAYJEIDJVF2FIGQTAYPMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BP556LEG3WENHZI5TAQ6ZEBFTJB4E2IS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CMNFX5MNYRWWIMO4BTKYQCGUDMHO3AXP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H472D5HPXN6RRXCNFML3BK5OYC52CXF2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/POPAEC4FWL4UU4LDEGPY5NPALU24FFQD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TAZZEVTCN2B4WT6AIBJ7XGYJMBTORJU5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XHTKU7YQ5EEP2XNSAV4M4VJ7QCBOJMOD/
- https://support.f5.com/csp/article/K02591030?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00014.html
- http://seclists.org/fulldisclosure/2019/Aug/16
- https://access.redhat.com/errata/RHSA-2019:2745
- https://access.redhat.com/errata/RHSA-2019:2746
- https://access.redhat.com/errata/RHSA-2019:2775
- https://access.redhat.com/errata/RHSA-2019:2799
- https://access.redhat.com/errata/RHSA-2019:2925
- https://access.redhat.com/errata/RHSA-2019:2939
- https://access.redhat.com/errata/RHSA-2019:2946
