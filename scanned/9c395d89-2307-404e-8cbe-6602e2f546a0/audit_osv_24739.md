# [M] Nextcloud Server and Enterprise Server missing brute force protection on password confirmation modal

## Summary
Severity: Medium
Advisory: CVE-2023-25820
Aliases: GHSA-36g6-wjx2-333x
CVSS: 4.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-03-22
Source: https://osv.dev/vulnerability/CVE-2023-25820
Type: osv

## Details
Nextcloud Server is the file server software for Nextcloud, a self-hosted productivity platform, and Nextcloud Enterprise Server is the enterprise version of the file server software. In Nextcloud Server versions 25.0.x prior to 25.0.5 and versions 24.0.x prior to 24.0.10 as well as Nextcloud Enterprise Server versions 25.0.x prior to 25.0.4, 24.0.x prior to 24.0.10, 23.0.x prior to 23.0.12.5, 22.x prior to 22.2.0.10, and 21.x prior to 21.0.9.10, when an attacker gets access to an already logged in user session they can then brute force the password on the confirmation endpoint. Nextcloud Server should upgraded to 24.0.10 or 25.0.4 and Nextcloud Enterprise Server should upgraded to 21.0.9.10, 22.2.10.10, 23.0.12.5, 24.0.10, or 25.0.4 to receive a patch. No known workarounds are available.

## References
- https://hackerone.com/reports/1842114
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25820.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-36g6-wjx2-333x
- https://nvd.nist.gov/vuln/detail/CVE-2023-25820
- https://github.com/nextcloud/server/pull/36489
