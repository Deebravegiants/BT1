# [M] RosarioSIS XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-287r-574x-f4h4
CVE: CVE-2021-45416
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-02-02
Source: https://github.com/advisories/GHSA-287r-574x-f4h4
Type: github-advisory

## Affected
- Packagist: `francoisjacquet/rosariosis` — affected >=0 <8.3

## Details
Reflected Cross-site scripting (XSS) vulnerability in RosarioSIS 8.2.1 allows attackers to inject arbitrary HTML via the search_term parameter in the modules/Scheduling/Courses.php script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45416
- https://github.com/86x/CVE-2021-45416
- https://gitlab.com/francoisjacquet/rosariosis/-/commit/aec018065ca12ecef03ee454a8112f992ea35315
- https://www.youtube.com/watch?v=PvFUxSGpWpY
- http://rosariosis.com
