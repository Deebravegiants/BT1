# [M] WWBN AVideo recovery notification bypass vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8m5f-2xvp-2c8w
CVE: CVE-2023-50172
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-8m5f-2xvp-2c8w
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
A recovery notification bypass vulnerability exists in the userRecoverPass.php captcha validation functionality of WWBN AVideo dev master commit 15fed957fb. A specially crafted HTTP request can lead to silently create a recovery pass code for any user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50172
- https://github.com/WWBN/AVideo/commit/15fed957fb64b4055158acfc449bd7974346edb5
- https://github.com/WWBN/AVideo
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1897
