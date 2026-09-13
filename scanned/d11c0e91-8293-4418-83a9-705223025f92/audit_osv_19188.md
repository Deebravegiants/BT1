# [H] CVE-2020-8616

## Summary
Severity: High
Advisory: CVE-2020-8616
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-8616
Type: osv

## Details
A malicious actor who intentionally exploits this lack of effective limitation on the number of fetches performed when processing referrals can, through the use of specially crafted referrals, cause a recursing server to issue a very large number of fetches in an attempt to process the referral. This has at least two potential effects: The performance of the recursing server can potentially be degraded by the additional work required to perform these fetches, and The attacker can exploit this behavior to use the recursing server as a reflector in a reflection attack with a high amplification factor.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00031.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JKJXVBOKZ36ER3EUCR7VRB7WGHIIMPNJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WOGCJS2XQ3SQNF4W6GLZ73LWZJ6ZZWZI/
- https://usn.ubuntu.com/4365-1/
- https://usn.ubuntu.com/4365-2/
- https://security.netapp.com/advisory/ntap-20200522-0002/
- https://www.debian.org/security/2020/dsa-4689
- https://www.synology.com/security/advisory/Synology_SA_20_12
- http://www.openwall.com/lists/oss-security/2020/05/19/4
- https://kb.isc.org/docs/cve-2020-8616
- http://www.nxnsattack.com
