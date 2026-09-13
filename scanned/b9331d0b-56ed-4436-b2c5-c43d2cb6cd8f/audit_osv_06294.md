# [H] BIT-libpython-2022-0391

## Summary
Severity: High
Advisory: BIT-libpython-2022-0391
Aliases: BIT-python-2022-0391, BIT-python-min-2022-0391, CVE-2022-0391, PSF-2022-8
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2022-0391
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.5

## Details
A flaw was found in Python, specifically within the urllib.parse module. This module helps break Uniform Resource Locator (URL) strings into components. The issue involves how the urlparse method does not sanitize input and allows characters like '\r' and '\n' in the URL path. This flaw allows an attacker to input a crafted URL, leading to injection attacks. This flaw affects Python versions prior to 3.10.0, 3.9.5, 3.8.11, 3.7.11 and 3.6.14.

## References
- https://bugs.python.org/issue43882
- https://lists.debian.org/debian-lts-announce/2023/09/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CSD2YBXP3ZF44E44QMIIAR5VTO35KTRB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UDBDBAU6HUPZHISBOARTXZ5GKHF2VH5U/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0391
- https://security.gentoo.org/glsa/202305-02
- https://security.netapp.com/advisory/ntap-20220225-0009/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00024.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00013.html
