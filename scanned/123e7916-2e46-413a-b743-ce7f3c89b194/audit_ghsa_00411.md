# [H] Android SVG vulnerable to XML External Entity (XXE)

## Summary
Severity: High
Advisory: GHSA-g556-x5vx-qh59
CVE: CVE-2017-1000498
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-g556-x5vx-qh59
Type: github-advisory

## Affected
- Maven: `com.caverock:androidsvg` — affected >=0 <1.3

## Details
AndroidSVG version 1.2.2 is vulnerable to XXE attacks in the SVG parsing component resulting in denial of service and possibly remote code execution

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000498
- https://github.com/BigBadaboom/androidsvg/issues/122
- https://github.com/BigBadaboom/androidsvg
- https://github.com/advisories/GHSA-g556-x5vx-qh59
