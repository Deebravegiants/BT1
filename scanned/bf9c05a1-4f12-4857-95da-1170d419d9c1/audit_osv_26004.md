# [H] Denial of Service in HTTP Collapsed Forwarding in Squid

## Summary
Severity: High
Advisory: CVE-2023-49288
Aliases: GHSA-rj5h-46j6-q2g5
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-12-04
Source: https://osv.dev/vulnerability/CVE-2023-49288
Type: osv

## Details
Squid is a caching proxy for the Web supporting HTTP, HTTPS, FTP, and more. Affected versions of squid are subject to a a Use-After-Free bug which can lead to a Denial of Service attack via collapsed forwarding. All versions of Squid from 3.5 up to and including 5.9 configured with "collapsed_forwarding on" are vulnerable. Configurations with "collapsed_forwarding off" or without a "collapsed_forwarding" directive are not vulnerable. This bug is fixed by Squid version 6.0.1. Users are advised to upgrade. Users unable to upgrade should remove all collapsed_forwarding lines from their squid.conf.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A5QASTMCUSUEW3UOMKHZJB3FTONWSRXS/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MEV66D3PAAY6K7TWDT3WZBLCPLASFJDC/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49288.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-rj5h-46j6-q2g5
- https://nvd.nist.gov/vuln/detail/CVE-2023-49288
- https://security.netapp.com/advisory/ntap-20240119-0006/
