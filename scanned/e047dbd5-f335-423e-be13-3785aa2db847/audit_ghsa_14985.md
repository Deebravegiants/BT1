# [M] Digital products download without proper payment status check

## Summary
Severity: Medium
Advisory: GHSA-v4g2-cm5v-cxv7
CVE: CVE-2024-37296
CWE: CWE-841
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-v4g2-cm5v-cxv7
Type: github-advisory

## Affected
- Packagist: `aimeos/ai-client-html` — affected >=2024.04.1 <2024.04.5
- Packagist: `aimeos/ai-client-html` — affected >=2023.04.1 <2023.10.14
- Packagist: `aimeos/ai-client-html` — affected >=2022.04.1 <2022.10.12
- Packagist: `aimeos/ai-client-html` — affected >=2021.04.1 <2021.10.21
- Packagist: `aimeos/ai-client-html` — affected >=2020.04.1 <2020.10.27

## Details
### Impact
Digital downloads sold in online shops can be downloaded without valid payment, e.g. if the payment didn't succeed.

### Patches
New versions for the Aimeos HTML client 2020-2024 are available

## References
- https://github.com/aimeos/ai-client-html/security/advisories/GHSA-v4g2-cm5v-cxv7
- https://nvd.nist.gov/vuln/detail/CVE-2024-37296
- https://github.com/aimeos/ai-client-html/commit/12d8aad1a373bf9d350872501adec3e222164f83
- https://github.com/aimeos/ai-client-html/commit/5a7249769142b3ce70959ab1fb70c7e7c251e214
- https://github.com/aimeos/ai-client-html/commit/6460ffe8f4929d864164aa96c5b49eca5326d975
- https://github.com/aimeos/ai-client-html/commit/7f01d2f4fbc67f5231fd84adeb835d28252b8409
- https://github.com/aimeos/ai-client-html/commit/fc611ff9a57e421d0ad9d99346b561cea515c5f0
- https://github.com/aimeos/ai-client-html
