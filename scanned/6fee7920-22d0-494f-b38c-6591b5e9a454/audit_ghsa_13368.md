# [H] TeamPass vulnerable to Improper Encoding or Escaping of Output

## Summary
Severity: High
Advisory: GHSA-2cv5-qvq3-6276
CVE: CVE-2023-3552
CWE: CWE-116
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-07-08
Source: https://github.com/advisories/GHSA-2cv5-qvq3-6276
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <3.0.10

## Details
TeamPass prior to 3.0.10 is vulnerable to cross-site scripting filter bypass in folder names. This can lead to information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3552
- https://github.com/nilsteampassnet/teampass/commit/8acb4dacc2d008a4186a4e13cc143e978f113955
- https://github.com/nilsteampassnet/teampass
- https://huntr.dev/bounties/aeb2f43f-0602-4ac6-9685-273e87ff4ded
