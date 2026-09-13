# [C] WWBN AVideo Insufficient Entropy vulnerbaility

## Summary
Severity: Critical
Advisory: GHSA-wqcc-qf63-c2x4
CVE: CVE-2023-49599
CWE: CWE-331
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-wqcc-qf63-c2x4
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
An insufficient entropy vulnerability exists in the salt generation functionality of WWBN AVideo dev master commit 15fed957fb. A specially crafted series of HTTP requests can lead to privilege escalation. An attacker can gather system information via HTTP requests and bruteforce the salt offline, leading to forging a legitimate password recovery code for the admin user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49599
- https://github.com/WWBN/AVideo/commit/15fed957fb64b4055158acfc449bd7974346edb5
- https://github.com/WWBN/AVideo
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1900
