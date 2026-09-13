# [H] CVE-2019-9513

## Summary
Severity: High
Advisory: CVE-2019-9513
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/CVE-2019-9513
Type: osv

## Details
Some HTTP/2 implementations are vulnerable to resource loops, potentially leading to a denial of service. The attacker creates multiple request streams and continually shuffles the priority of the streams in a way that causes substantial churn to the priority tree. This can consume excess CPU.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ZQGHE3WTYLYAYJEIDJVF2FIGQTAYPMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CMNFX5MNYRWWIMO4BTKYQCGUDMHO3AXP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JUBYAF6ED3O4XCHQ5C2HYENJLXYXZC4M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LZLUYPYY3RX4ZJDWZRJIKSULYRJ4PXW7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/POPAEC4FWL4UU4LDEGPY5NPALU24FFQD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TAZZEVTCN2B4WT6AIBJ7XGYJMBTORJU5/
- https://support.f5.com/csp/article/K02591030?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00014.html
- https://access.redhat.com/errata/RHSA-2019:2692
- https://access.redhat.com/errata/RHSA-2019:2745
- https://access.redhat.com/errata/RHSA-2019:2746
- https://access.redhat.com/errata/RHSA-2019:2775
- https://access.redhat.com/errata/RHSA-2019:2799
- https://access.redhat.com/errata/RHSA-2019:2925
- https://access.redhat.com/errata/RHSA-2019:2939
