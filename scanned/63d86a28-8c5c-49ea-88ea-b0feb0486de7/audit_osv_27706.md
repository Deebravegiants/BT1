# [H] SQUID-2024:1 Denial of Service in HTTP Chunked Decoding

## Summary
Severity: High
Advisory: CVE-2024-25111
Aliases: GHSA-72c2-c3wm-8qxc
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2024-25111
Type: osv

## Details
Squid is a web proxy cache. Starting in version 3.5.27 and prior to version 6.8, Squid may be vulnerable to a Denial of Service attack against HTTP Chunked decoder due to an uncontrolled recursion bug. This problem allows a remote attacker to cause Denial of Service when sending a crafted, chunked, encoded HTTP Message. This bug is fixed in Squid version 6.8. In addition, patches addressing this problem for the stable releases can be found in Squid's patch archives. There is no workaround for this issue.

## References
- http://www.squid-cache.org/Versions/v6/SQUID-2024_1.patch
- https://lists.debian.org/debian-lts-announce/2025/03/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7R4KPSO3MQT3KAOZV7LC2GG3CYMCGK7H/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWQHRDRHDM5PQTU6BHH4C5KGL37X6TVI/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25111.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-72c2-c3wm-8qxc
- https://nvd.nist.gov/vuln/detail/CVE-2024-25111
- https://security.netapp.com/advisory/ntap-20240605-0001/
