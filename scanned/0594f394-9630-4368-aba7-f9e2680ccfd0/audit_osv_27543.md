# [M] SQUID-2023:11 Denial of Service in Cache Manager

## Summary
Severity: Medium
Advisory: CVE-2024-23638
Aliases: GHSA-j49p-553x-48rx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-23638
Type: osv

## Details
Squid is a caching proxy for the Web. Due to an expired pointer reference bug, Squid prior to version 6.6 is vulnerable to a Denial of Service attack against Cache Manager error responses. This problem allows a trusted client to perform Denial of Service when generating error pages for Client Manager reports. Squid older than 5.0.5 have not been tested and should be assumed to be vulnerable. All Squid-5.x up to and including 5.9 are vulnerable. All Squid-6.x up to and including 6.5 are vulnerable. This bug is fixed by Squid version 6.6. In addition, patches addressing this problem for the stable releases can be found in Squid's patch archives. As a workaround, prevent access to Cache Manager using Squid's main access control: `http_access deny manager`.

## References
- http://www.squid-cache.org/Versions/v5/SQUID-2023_11.patch
- http://www.squid-cache.org/Versions/v6/SQUID-2023_11.patch
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7R4KPSO3MQT3KAOZV7LC2GG3CYMCGK7H/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWQHRDRHDM5PQTU6BHH4C5KGL37X6TVI/
- https://megamansec.github.io/Squid-Security-Audit/stream-assert.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23638.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-j49p-553x-48rx
- https://nvd.nist.gov/vuln/detail/CVE-2024-23638
- https://security.netapp.com/advisory/ntap-20240208-0010/
- https://github.com/squid-cache/squid/commit/290ae202883ac28a48867079c2fb34c40efd382b
- https://github.com/squid-cache/squid/commit/e8118a7381213f5cfcdeb4cec1d2d854bfd261c8
