# [M] phpThumb is vulnerable to Command Injection through its gif_outputAsJpeg function

## Summary
Severity: Medium
Advisory: GHSA-q745-cfqh-hcrw
CVE: CVE-2025-52994
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-11
Source: https://github.com/advisories/GHSA-q745-cfqh-hcrw
Type: github-advisory

## Affected
- Packagist: `james-heinrich/phpthumb` — affected >=0

## Details
gif_outputAsJpeg in phpThumb through 1.7.23 allows phpthumb.gif.php OS Command Injection via a crafted parameter value. This is fixed in 1.7.23-202506081709.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52994
- https://github.com/JamesHeinrich/phpThumb/commit/cdcbc206ae601b15fd17e7aadf59df51149a0e82
- https://github.com/JamesHeinrich/phpThumb
- https://github.com/JamesHeinrich/phpThumb/releases
- https://safety-online.pl/cve-2025-52994
