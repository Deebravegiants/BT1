# [H] CVE-2022-26357

## Summary
Severity: High
Advisory: CVE-2022-26357
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2022-26357
Type: osv

## Details
race in VT-d domain ID cleanup Xen domain IDs are up to 15 bits wide. VT-d hardware may allow for only less than 15 bits to hold a domain ID associating a physical device with a particular domain. Therefore internally Xen domain IDs are mapped to the smaller value range. The cleaning up of the housekeeping structures has a race, allowing for VT-d domain IDs to be leaked and flushes to be bypassed.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6ETPM2OVZZ6KOS2L7QO7SIW6XWT5OW3F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHFSRVLM2JUCPDC2KGB7ETPQYJLCGBLD/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5117
- https://xenbits.xenproject.org/xsa/advisory-399.txt
- http://www.openwall.com/lists/oss-security/2022/04/05/2
- http://xenbits.xen.org/xsa/advisory-399.html
