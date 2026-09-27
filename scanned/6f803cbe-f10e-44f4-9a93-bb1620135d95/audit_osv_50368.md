# [H] CVE-2020-14305

## Summary
Severity: High
Advisory: CVE-2020-14305
Aliases: A-174904512, ASB-A-174904512
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-14305
Type: osv

## Details
An out-of-bounds memory write flaw was found in how the Linux kernel’s Voice Over IP H.323 connection tracking functionality handled connections on ipv6 port 1720. This flaw allows an unauthenticated remote user to crash the system, causing a denial of service. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://patchwork.ozlabs.org/project/netfilter-devel/patch/c2385b5c-309c-cc64-2e10-a0ef62897502%40virtuozzo.com/
- https://security.netapp.com/advisory/ntap-20201210-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=1850716
- https://bugs.openvz.org/browse/OVZ-7188
