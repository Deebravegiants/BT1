# [H] CVE-2022-45188

## Summary
Severity: High
Advisory: CVE-2022-45188
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-12
Source: https://osv.dev/vulnerability/CVE-2022-45188
Type: osv

## Details
Netatalk through 3.1.13 has an afp_getappl heap-based buffer overflow resulting in code execution via a crafted .appl file. This provides remote root access on some platforms such as FreeBSD (used for TrueNAS).

## References
- https://netatalk.sourceforge.io/3.1/ReleaseNotes3.1.13.html
- https://netatalk.sourceforge.io/3.1/ReleaseNotes3.1.14.html
- https://rushbnt.github.io/bug%20analysis/netatalk-0day/
- https://sourceforge.net/projects/netatalk/files/netatalk/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45188.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZYWSGVA6WXREMB6PV56HAHKU7R6KPOP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GEAFLA5L2SHOUFBAGUXIF2TZLGBXGJKT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SG6WZW5LXFVH3P7ZVZRGHUVJEMEFKQLI/
- https://nvd.nist.gov/vuln/detail/CVE-2022-45188
- https://security.gentoo.org/glsa/202311-02
- https://www.debian.org/security/2023/dsa-5503
- https://lists.debian.org/debian-lts-announce/2023/05/msg00018.html
