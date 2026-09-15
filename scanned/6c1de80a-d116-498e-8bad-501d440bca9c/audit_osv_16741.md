# [H] CVE-2019-9511

## Summary
Severity: High
Advisory: CVE-2019-9511
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/CVE-2019-9511
Type: osv

## Details
Some HTTP/2 implementations are vulnerable to window size manipulation and stream prioritization manipulation, potentially leading to a denial of service. The attacker requests a large amount of data from a specified resource over multiple streams. They manipulate window size and stream priority to force the server to queue the data in 1-byte chunks. Depending on how efficiently this data is queued, this can consume excess CPU, memory, or both.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BP556LEG3WENHZI5TAQ6ZEBFTJB4E2IS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JUBYAF6ED3O4XCHQ5C2HYENJLXYXZC4M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LZLUYPYY3RX4ZJDWZRJIKSULYRJ4PXW7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/POPAEC4FWL4UU4LDEGPY5NPALU24FFQD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TAZZEVTCN2B4WT6AIBJ7XGYJMBTORJU5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XHTKU7YQ5EEP2XNSAV4M4VJ7QCBOJMOD/
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
