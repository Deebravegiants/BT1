# [H] Nextcloud server allows the by-pass the second factor

## Summary
Severity: High
Advisory: CVE-2024-37313
Aliases: GHSA-9v72-9xv5-3p7c
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-06-14
Source: https://osv.dev/vulnerability/CVE-2024-37313
Type: osv

## Details
Nextcloud server is a self hosted personal cloud system. Under some circumstance it was possible to bypass the second factor of 2FA after successfully providing the user credentials. It is recommended that the Nextcloud Server is upgraded to 26.0.13, 27.1.8 or 28.0.4 and Nextcloud Enterprise Server is upgraded to 21.0.9.17, 22.2.10.22, 23.0.12.17, 24.0.12.13, 25.0.13.8, 26.0.13, 27.1.8 or 28.0.4.

## References
- https://hackerone.com/reports/2419776
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37313.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-9v72-9xv5-3p7c
- https://nvd.nist.gov/vuln/detail/CVE-2024-37313
- https://github.com/nextcloud/server/pull/44276
