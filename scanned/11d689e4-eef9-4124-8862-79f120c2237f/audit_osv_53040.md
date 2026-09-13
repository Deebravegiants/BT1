# [M] CVE-2022-26364

## Summary
Severity: Medium
Advisory: CVE-2022-26364
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/CVE-2022-26364
Type: osv

## Details
x86 pv: Insufficient care with non-coherent mappings T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Xen maintains a type reference count for pages, in addition to a regular reference count. This scheme is used to maintain invariants required for Xen's safety, e.g. PV guests may not have direct writeable access to pagetables; updates need auditing by Xen. Unfortunately, Xen's safety logic doesn't account for CPU-induced cache non-coherency; cases where the CPU can cause the content of the cache to be different to the content in main memory. In such cases, Xen's safety logic can incorrectly conclude that the contents of a page is safe.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RKRXZ4LHGCGMOG24ZCEJNY6R2BTS4S2Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OH65U6FTTB5MLH5A6Q3TW7KVCGOG4MYI/
- https://security.gentoo.org/glsa/202208-23
- https://www.debian.org/security/2022/dsa-5184
- https://xenbits.xenproject.org/xsa/advisory-402.txt
- http://www.openwall.com/lists/oss-security/2022/06/09/4
- http://xenbits.xen.org/xsa/advisory-402.html
- http://packetstormsecurity.com/files/167710/Xen-PV-Guest-Non-SELFSNOOP-CPU-Memory-Corruption.html
