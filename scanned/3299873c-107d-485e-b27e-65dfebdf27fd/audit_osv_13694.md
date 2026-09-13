# [H] CVE-2018-20843

## Summary
Severity: High
Advisory: CVE-2018-20843
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-24
Source: https://osv.dev/vulnerability/CVE-2018-20843
Type: osv

## Details
In libexpat in Expat before 2.2.7, XML input including XML names that contain a large number of colons could make the XML parser consume a high amount of RAM and CPU resources while processing (enough to be usable for denial-of-service attacks).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CEJJSQSG3KSUQY4FPVHZ7ZTT7FORMFVD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IDAUGEB3TUP6NEKJDBUBZX7N5OAUOOOK/
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00039.html
- https://github.com/libexpat/libexpat/blob/R_2_2_7/expat/Changes
- https://lists.debian.org/debian-lts-announce/2019/06/msg00028.html
- https://seclists.org/bugtraq/2019/Jun/39
- https://security.gentoo.org/glsa/201911-08
- https://security.netapp.com/advisory/ntap-20190703-0001/
- https://support.f5.com/csp/article/K51011533
- https://usn.ubuntu.com/4040-1/
- https://usn.ubuntu.com/4040-2/
- https://www.debian.org/security/2019/dsa-4472
- https://www.tenable.com/security/tns-2021-11
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5226
- https://github.com/libexpat/libexpat/issues/186
- https://github.com/libexpat/libexpat/pull/262
- https://github.com/libexpat/libexpat/pull/262/commits/11f8838bf99ea0a6f0b76f9760c43704d00c4ff6
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
