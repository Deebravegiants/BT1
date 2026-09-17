# [M] CVE-2020-15563

## Summary
Severity: Medium
Advisory: CVE-2020-15563
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/CVE-2020-15563
Type: osv

## Details
An issue was discovered in Xen through 4.13.x, allowing x86 HVM guest OS users to cause a hypervisor crash. An inverted conditional in x86 HVM guests' dirty video RAM tracking code allows such guests to make Xen de-reference a pointer guaranteed to point at unmapped space. A malicious or buggy HVM guest may cause the hypervisor to crash, resulting in Denial of Service (DoS) affecting the entire host. Xen versions from 4.8 onwards are affected. Xen versions 4.7 and earlier are not affected. Only x86 systems are affected. Arm systems are not affected. Only x86 HVM guests using shadow paging can leverage the vulnerability. In addition, there needs to be an entity actively monitoring a guest's video frame buffer (typically for display purposes) in order for such a guest to be able to leverage the vulnerability. x86 PV guests, as well as x86 HVM guests using hardware assisted paging (HAP), cannot leverage the vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MXESCOVI7AVRNC7HEAMFM7PMEO6D3AUH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VB3QJJZV23Z2IDYEMIHELWYSQBUEW6JP/
- https://security.gentoo.org/glsa/202007-02
- https://www.debian.org/security/2020/dsa-4723
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00031.html
- http://www.openwall.com/lists/oss-security/2020/07/07/3
- http://xenbits.xen.org/xsa/advisory-319.html
