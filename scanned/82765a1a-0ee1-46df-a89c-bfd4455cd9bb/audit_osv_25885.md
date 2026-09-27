# [H] SQUID-2023:4 Denial of Service in SSL Certificate validation

## Summary
Severity: High
Advisory: CVE-2023-46724
Aliases: GHSA-73m6-jm96-c6r3
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-11-01
Source: https://osv.dev/vulnerability/CVE-2023-46724
Type: osv

## Details
Squid is a caching proxy for the Web. Due to an Improper Validation of Specified Index bug, Squid versions 3.3.0.1 through 5.9 and 6.0 prior to 6.4 compiled using `--with-openssl` are vulnerable to a Denial of Service attack against SSL Certificate validation. This problem allows a remote server to perform Denial of Service against Squid Proxy by initiating a TLS Handshake with a specially crafted SSL Certificate in a server certificate chain. This attack is limited to HTTPS and SSL-Bump. This bug is fixed in Squid version 6.4. In addition, patches addressing this problem for the stable releases can be found in Squid's patch archives. Those who you use a prepackaged version of Squid should refer to the package vendor for availability information on updated packages.

## References
- http://www.squid-cache.org/Versions/v5/SQUID-2023_4.patch
- http://www.squid-cache.org/Versions/v6/SQUID-2023_4.patch
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A5QASTMCUSUEW3UOMKHZJB3FTONWSRXS/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MEV66D3PAAY6K7TWDT3WZBLCPLASFJDC/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46724.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-73m6-jm96-c6r3
- https://nvd.nist.gov/vuln/detail/CVE-2023-46724
- https://security.netapp.com/advisory/ntap-20231208-0001/
- https://github.com/squid-cache/squid/commit/b70f864940225dfe69f9f653f948e787f99c3810
