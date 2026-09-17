# [H] Denial of Service in HTTP Message Processing in Squid

## Summary
Severity: High
Advisory: CVE-2023-49285
Aliases: GHSA-8w9r-p88v-mmx9
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-12-04
Source: https://osv.dev/vulnerability/CVE-2023-49285
Type: osv

## Details
Squid is a caching proxy for the Web supporting HTTP, HTTPS, FTP, and more. Due to a Buffer Overread bug Squid is vulnerable to a Denial of Service attack against Squid HTTP Message processing. This bug is fixed by Squid version 6.5. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- http://www.squid-cache.org/Versions/v5/SQUID-2023_7.patch
- http://www.squid-cache.org/Versions/v6/SQUID-2023_7.patch
- https://lists.debian.org/debian-lts-announce/2024/01/msg00003.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A5QASTMCUSUEW3UOMKHZJB3FTONWSRXS/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MEV66D3PAAY6K7TWDT3WZBLCPLASFJDC/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49285.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-8w9r-p88v-mmx9
- https://nvd.nist.gov/vuln/detail/CVE-2023-49285
- https://security.netapp.com/advisory/ntap-20240119-0004/
- https://github.com/squid-cache/squid/commit/77b3fb4df0f126784d5fd4967c28ed40eb8d521b
- https://github.com/squid-cache/squid/commit/deee944f9a12c9fd399ce52f3e2526bb573a9470
