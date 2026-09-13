# [H] CVE-2017-11600

## Summary
Severity: High
Advisory: CVE-2017-11600
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-24
Source: https://osv.dev/vulnerability/CVE-2017-11600
Type: osv

## Details
net/xfrm/xfrm_policy.c in the Linux kernel through 4.12.3, when CONFIG_XFRM_MIGRATE is enabled, does not ensure that the dir value of xfrm_userpolicy_id is XFRM_POLICY_MAX or less, which allows local users to cause a denial of service (out-of-bounds access) or possibly have unspecified other impact via an XFRM_MSG_MIGRATE xfrm Netlink message.

## References
- http://www.securityfocus.com/bid/99928
- https://access.redhat.com/errata/RHSA-2018:2003
- https://access.redhat.com/errata/RHSA-2019:1170
- https://source.android.com/security/bulletin/pixel/2017-11-01
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- http://seclists.org/bugtraq/2017/Jul/30
- http://www.debian.org/security/2017/dsa-3981
- https://access.redhat.com/errata/RHSA-2018:1965
- https://access.redhat.com/errata/RHSA-2019:1190
