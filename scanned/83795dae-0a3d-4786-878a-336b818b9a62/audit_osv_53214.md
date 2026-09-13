# [H] CVE-2022-33742

## Summary
Severity: High
Advisory: CVE-2022-33742
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/CVE-2022-33742
Type: osv

## Details
Linux disk/nic frontends data leaks T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Linux Block and Network PV device frontends don't zero memory regions before sharing them with the backend (CVE-2022-26365, CVE-2022-33740). Additionally the granularity of the grant table doesn't allow sharing less than a 4K page, leading to unrelated data residing in the same 4K page as data shared with a backend being accessible by such backend (CVE-2022-33741, CVE-2022-33742).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RKRXZ4LHGCGMOG24ZCEJNY6R2BTS4S2Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IGFTRZ66KQYTSYIRT5FRHF5D6O72NWOP/
- https://www.debian.org/security/2022/dsa-5191
- https://xenbits.xenproject.org/xsa/advisory-403.txt
- https://lists.debian.org/debian-lts-announce/2022/10/msg00000.html
- http://www.openwall.com/lists/oss-security/2022/07/05/6
- http://xenbits.xen.org/xsa/advisory-403.html
