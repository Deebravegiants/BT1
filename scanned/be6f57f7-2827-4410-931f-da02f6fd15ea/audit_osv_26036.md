# [M] Bruteforce protection can be bypassed with misconfigured proxy

## Summary
Severity: Medium
Advisory: CVE-2023-49792
Aliases: GHSA-5j2p-q736-hw98
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-12-22
Source: https://osv.dev/vulnerability/CVE-2023-49792
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. In Nextcloud Server prior to versions 26.0.9 and 27.1.4; as well as Nextcloud Enterprise Server prior to versions 23.0.12.13, 24.0.12.9, 25.0.13.4, 26.0.9, and 27.1.4; when a (reverse) proxy is configured as trusted proxy the server could be tricked into reading a wrong remote address for an attacker, allowing them executing authentication attempts than intended. Nextcloud Server versions 26.0.9 and 27.1.4 and Nextcloud Enterprise Server versions 23.0.12.13, 24.0.12.9, 25.0.13.4, 26.0.9, and 27.1.4 contain a patch for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/2230915
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49792.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-5j2p-q736-hw98
- https://nvd.nist.gov/vuln/detail/CVE-2023-49792
- https://github.com/nextcloud/server/pull/41526
