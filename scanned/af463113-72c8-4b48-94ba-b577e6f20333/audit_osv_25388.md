# [H] Nextcloud Server password reset endpoint is not brute force protected

## Summary
Severity: High
Advisory: CVE-2023-35172
Aliases: GHSA-mjf5-p765-qmr6
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-06-23
Source: https://osv.dev/vulnerability/CVE-2023-35172
Type: osv

## Details
NextCloud Server and NextCloud Enterprise Server provide file storage for Nextcloud, a self-hosted productivity platform. In NextCloud Server versions 25.0.0 until 25.0.7 and 26.0.0 until 26.0.2 and Nextcloud Enterprise Server versions 21.0.0 until 21.0.9.12, 22.0.0 until 22.2.10.12, 23.0.0 until 23.0.12.7, 24.0.0 until 24.0.12.2, 25.0.0 until 25.0.7, and 26.0.0 until 26.0.2, an attacker can bruteforce the password reset links. Nextcloud Server n 25.0.7 and 26.0.2 and Nextcloud Enterprise Server 21.0.9.12, 22.2.10.12, 23.0.12.7, 24.0.12.2, 25.0.7, and 26.0.2 contain a patch for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/1987062
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35172.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-mjf5-p765-qmr6
- https://nvd.nist.gov/vuln/detail/CVE-2023-35172
- https://github.com/nextcloud/server/pull/38267
