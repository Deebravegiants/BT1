# [M] CVE-2017-6410

## Summary
Severity: Medium
Advisory: CVE-2017-6410
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2017-6410
Type: osv

## Details
kpac/script.cpp in KDE kio before 5.32 and kdelibs before 4.14.30 calls the PAC FindProxyForURL function with a full https URL (potentially including Basic Authentication credentials, a query string, or PATH_INFO), which allows remote attackers to obtain sensitive information via a crafted PAC file.

## References
- http://www.securityfocus.com/bid/96515
- http://www.debian.org/security/2017/dsa-3849
- https://www.kde.org/info/security/advisory-20170228-1.txt
