# [H] SQUID-2023:10 Denial of Service in HTTP Request parsing

## Summary
Severity: High
Advisory: CVE-2023-50269
Aliases: GHSA-wgq4-4cfg-c4x3
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-50269
Type: osv

## Details
Squid is a caching proxy for the Web. Due to an Uncontrolled Recursion bug in versions 2.6 through 2.7.STABLE9, versions 3.1 through 5.9, and versions 6.0.1 through 6.5, Squid may be vulnerable to a Denial of Service attack against HTTP Request parsing. This problem allows a remote client to perform Denial of Service attack by sending a large X-Forwarded-For header when the follow_x_forwarded_for feature is configured. This bug is fixed by Squid version 6.6. In addition, patches addressing this problem for the stable releases can be found in Squid's patch archives.

## References
- http://www.squid-cache.org/Versions/v5/SQUID-2023_10.patch
- http://www.squid-cache.org/Versions/v6/SQUID-2023_10.patch
- https://lists.debian.org/debian-lts-announce/2024/01/msg00003.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A5QASTMCUSUEW3UOMKHZJB3FTONWSRXS/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MEV66D3PAAY6K7TWDT3WZBLCPLASFJDC/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50269.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-wgq4-4cfg-c4x3
- https://nvd.nist.gov/vuln/detail/CVE-2023-50269
- https://security.netapp.com/advisory/ntap-20240119-0005/
