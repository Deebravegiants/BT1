# [M] Exposure of Resource to Wrong Sphere in microweber

## Summary
Severity: Medium
Advisory: GHSA-5875-p652-2ppm
CVE: CVE-2022-0762
CWE: CWE-668, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-27
Source: https://github.com/advisories/GHSA-5875-p652-2ppm
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.3.0

## Details
Exposure of Resource to Wrong Sphere in microweber prior to 1.3 allows users to add deleted products to a cart and buy it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0762
- https://github.com/microweber/microweber/commit/76361264d9fdfff38a1af79c63141455cc4d36e3
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/125b5244-5099-485e-bf75-e5f1ed80dd48
