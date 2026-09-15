# [H] CVE-2015-7547

## Summary
Severity: High
Advisory: CVE-2015-7547
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-02-18
Source: https://osv.dev/vulnerability/CVE-2015-7547
Type: osv

## Details
Multiple stack-based buffer overflows in the (1) send_dg and (2) send_vc functions in the libresolv library in the GNU C Library (aka glibc or libc6) before 2.23 allow remote attackers to cause a denial of service (crash) or possibly execute arbitrary code via a crafted DNS response that triggers a call to the getaddrinfo function with the AF_UNSPEC or AF_INET6 address family, related to performing "dual A/AAAA DNS queries" and the libnss_dns.so.2 NSS module.

## References
- http://fortiguard.com/advisory/glibc-getaddrinfo-stack-overflow
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00043.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00044.html
- http://rhn.redhat.com/errata/RHSA-2016-0175.html
- http://rhn.redhat.com/errata/RHSA-2016-0176.html
- http://rhn.redhat.com/errata/RHSA-2016-0225.html
- http://rhn.redhat.com/errata/RHSA-2016-0277.html
- http://ubuntu.com/usn/usn-2900-1
- http://www.debian.org/security/2016/dsa-3480
- http://www.debian.org/security/2016/dsa-3481
- http://www.fortiguard.com/advisory/glibc-getaddrinfo-stack-overflow
- http://www.huawei.com/en/psirt/security-advisories/huawei-sa-20160304-01-glibc-en
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.vmware.com/security/advisories/VMSA-2016-0002.html
