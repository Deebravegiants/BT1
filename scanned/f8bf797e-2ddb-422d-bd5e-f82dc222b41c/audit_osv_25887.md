# [H] SQUID-2021:8 Denial of Service in Gopher gateway

## Summary
Severity: High
Advisory: CVE-2023-46728
Aliases: GHSA-cg5h-v6vc-w33f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-46728
Type: osv

## Details
Squid is a caching proxy for the Web supporting HTTP, HTTPS, FTP, and more. Due to a NULL pointer dereference bug Squid is vulnerable to a Denial of Service attack against Squid's Gopher gateway. The gopher protocol is always available and enabled in Squid prior to Squid 6.0.1. Responses triggering this bug are possible to be received from any gopher server, even those without malicious intent. Gopher support has been removed in Squid version 6.0.1. Users are advised to upgrade. Users unable to upgrade should reject all gopher URL requests.

## References
- https://lists.debian.org/debian-lts-announce/2025/09/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A5QASTMCUSUEW3UOMKHZJB3FTONWSRXS/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MEV66D3PAAY6K7TWDT3WZBLCPLASFJDC/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46728.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-cg5h-v6vc-w33f
- https://nvd.nist.gov/vuln/detail/CVE-2023-46728
- https://security.netapp.com/advisory/ntap-20231214-0006/
- https://github.com/squid-cache/squid/commit/6ea12e8fb590ac6959e9356a81aa3370576568c3
