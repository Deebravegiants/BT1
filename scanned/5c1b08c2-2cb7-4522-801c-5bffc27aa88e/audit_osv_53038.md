# [M] CVE-2022-26362

## Summary
Severity: Medium
Advisory: CVE-2022-26362
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/CVE-2022-26362
Type: osv

## Details
x86 pv: Race condition in typeref acquisition Xen maintains a type reference count for pages, in addition to a regular reference count. This scheme is used to maintain invariants required for Xen's safety, e.g. PV guests may not have direct writeable access to pagetables; updates need auditing by Xen. Unfortunately, the logic for acquiring a type reference has a race condition, whereby a safely TLB flush is issued too early and creates a window where the guest can re-establish the read/write mapping before writeability is prohibited.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OH65U6FTTB5MLH5A6Q3TW7KVCGOG4MYI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RKRXZ4LHGCGMOG24ZCEJNY6R2BTS4S2Q/
- https://security.gentoo.org/glsa/202208-23
- https://www.debian.org/security/2022/dsa-5184
- https://xenbits.xenproject.org/xsa/advisory-401.txt
- http://packetstormsecurity.com/files/167718/Xen-TLB-Flush-Bypass.html
- http://www.openwall.com/lists/oss-security/2022/06/09/3
- http://xenbits.xen.org/xsa/advisory-401.html
