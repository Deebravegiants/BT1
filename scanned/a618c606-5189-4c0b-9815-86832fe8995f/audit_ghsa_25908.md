# [H] Exposure of Resource to Wrong Sphere in ThinkPHP Framework

## Summary
Severity: High
Advisory: GHSA-69wp-xwm7-69wm
CVE: CVE-2022-25481
CWE: CWE-284, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-22
Source: https://github.com/advisories/GHSA-69wp-xwm7-69wm
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected >=0

## Details
ThinkPHP Framework v5.0.24 was discovered to be configured without the PATHINFO parameter. This allows attackers to access all system environment parameters from index.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25481
- https://github.com/Lyther/VulnDiscover/blob/master/Web/ThinkPHP_InfoLeak.md
- https://github.com/top-think/framework
