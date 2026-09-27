# [M] Buffer Underwrite in ares_inet_net_pton()

## Summary
Severity: Medium
Advisory: CVE-2023-31130
Aliases: GHSA-x6mf-cxr9-8q6v
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/CVE-2023-31130
Type: osv

## Details
c-ares is an asynchronous resolver library. ares_inet_net_pton() is vulnerable to a buffer underflow for certain ipv6 addresses, in particular "0::00:00:00/2" was found to cause an issue.  C-ares only uses this function internally for configuration purposes which would require an administrator to configure such an address via ares_set_sortlist(). However, users may externally use ares_inet_net_pton() for other purposes and thus be vulnerable to more severe issues. This issue has been fixed in 1.19.1.

## References
- https://github.com/c-ares/c-ares/releases/tag/cares-1_19_1
- https://lists.debian.org/debian-lts-announce/2023/06/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B5Z5XFNXTNPTCBBVXFDNZQVLLIE6VRBY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBFWILTA33LOSV23P44FGTQQIDRJHIY7/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31130.json
- https://github.com/c-ares/c-ares/security/advisories/GHSA-x6mf-cxr9-8q6v
- https://nvd.nist.gov/vuln/detail/CVE-2023-31130
- https://security.gentoo.org/glsa/202310-09
- https://security.netapp.com/advisory/ntap-20240605-0005/
- https://www.debian.org/security/2023/dsa-5419
