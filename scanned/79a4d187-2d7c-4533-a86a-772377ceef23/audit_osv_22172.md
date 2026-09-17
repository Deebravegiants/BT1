# [M] CVE-2022-23123

## Summary
Severity: Medium
Advisory: CVE-2022-23123
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-03-28
Source: https://osv.dev/vulnerability/CVE-2022-23123
Type: osv

## Details
This vulnerability allows remote attackers to disclose sensitive information on affected installations of Netatalk. Authentication is not required to exploit this vulnerability. The specific flaw exists within the getdirparams method. The issue results from the lack of proper validation of user-supplied data, which can result in a read past the end of an allocated buffer. An attacker can leverage this in conjunction with other vulnerabilities to execute arbitrary code in the context of root. Was ZDI-CAN-15830.

## References
- https://netatalk.sourceforge.io/3.1/ReleaseNotes3.1.13.html
- https://www.kb.cert.org/vuls/id/709991
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23123.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-23123
- https://security.gentoo.org/glsa/202311-02
- https://www.debian.org/security/2023/dsa-5503
- https://www.zerodayinitiative.com/advisories/ZDI-22-528/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00018.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00016.html
