# [H] CVE-2020-25599

## Summary
Severity: High
Advisory: CVE-2020-25599
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/CVE-2020-25599
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. There are evtchn_reset() race conditions. Uses of EVTCHNOP_reset (potentially by a guest on itself) or XEN_DOMCTL_soft_reset (by itself covered by XSA-77) can lead to the violation of various internal assumptions. This may lead to out of bounds memory accesses or triggering of bug checks. In particular, x86 PV guests may be able to elevate their privilege to that of the host. Host and guest crashes are also possible, leading to a Denial of Service (DoS). Information leaks cannot be ruled out. All Xen versions from 4.5 onwards are vulnerable. Xen versions 4.4 and earlier are not vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DA633Y3G5KX7MKRN4PFEGM3IVTJMBEOM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJZERRBJN6E6STDCHT4JHP4MI6TKBCJE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4JRXMKEMQRQYWYEPHVBIWUEAVQ3LU4FN/
- https://security.gentoo.org/glsa/202011-06
- https://www.debian.org/security/2020/dsa-4769
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00008.html
- http://www.openwall.com/lists/oss-security/2020/12/16/5
- https://xenbits.xen.org/xsa/advisory-343.html
