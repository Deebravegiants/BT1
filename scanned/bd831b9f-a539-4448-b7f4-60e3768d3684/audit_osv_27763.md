# [M] Denial of Service in HTTP Header parser in squid proxy

## Summary
Severity: Medium
Advisory: CVE-2024-25617
Aliases: GHSA-h5x6-w8mv-xfpr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/CVE-2024-25617
Type: osv

## Details
Squid is an open source caching proxy for the Web supporting HTTP, HTTPS, FTP, and more. Due to a Collapse of Data into Unsafe Value bug ,Squid may be vulnerable to a Denial of Service attack against HTTP header parsing. This problem allows a remote client or a remote server to perform Denial of Service when sending oversized headers in HTTP messages. In versions of Squid prior to 6.5 this can be achieved if the request_header_max_size or reply_header_max_size settings are unchanged from the default. In Squid version 6.5 and later, the default setting of these parameters is safe. Squid will emit a critical warning in cache.log if the administrator is setting these parameters to unsafe values. Squid will not at this time prevent these settings from being changed to unsafe values. Users are advised to upgrade to version 6.5. There are no known workarounds for this vulnerability. This issue is also tracked as SQUID-2024:2

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25617.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-h5x6-w8mv-xfpr
- https://nvd.nist.gov/vuln/detail/CVE-2024-25617
- https://security.netapp.com/advisory/ntap-20240322-0006/
- https://github.com/squid-cache/squid/commit/72a3bbd5e431597c3fdb56d752bc56b010ba3817
