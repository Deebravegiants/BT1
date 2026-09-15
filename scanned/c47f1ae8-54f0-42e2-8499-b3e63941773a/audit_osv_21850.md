# [C] CVE-2022-0194

## Summary
Severity: Critical
Advisory: CVE-2022-0194
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-28
Source: https://osv.dev/vulnerability/CVE-2022-0194
Type: osv

## Details
This vulnerability allows remote attackers to execute arbitrary code on affected installations of Netatalk. Authentication is not required to exploit this vulnerability. The specific flaw exists within the ad_addcomment function. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length stack-based buffer. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-15876.

## References
- https://netatalk.sourceforge.io/3.1/ReleaseNotes3.1.13.html
- https://www.kb.cert.org/vuls/id/709991
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0194.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0194
- https://security.gentoo.org/glsa/202311-02
- https://www.debian.org/security/2023/dsa-5503
- https://www.zerodayinitiative.com/advisories/ZDI-22-530/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00018.html
