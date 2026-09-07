# [M] AVideo cross-site scripting vulnerability in the view/about.php page

## Summary
Severity: Medium
Advisory: GHSA-f98p-2hc5-fm7v
CVE: CVE-2024-34899
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-f98p-2hc5-fm7v
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <14.3

## Details
The PHP file view/about.php is vulnerable to an XSS issue due to no sanitization of the user agent.

At line [53], the website gets the user-agent from the headers through $_SERVER['HTTP_USER_AGENT'] and echo it without any sanitization.

In PHP, echo a user generated statement, here the User-Agent Header, without any sanitization allows an attacker to inject malicious scripts into the output of a web page, which are then executed in the browser of anyone viewing that page.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-f98p-2hc5-fm7v
- https://nvd.nist.gov/vuln/detail/CVE-2024-34899
- https://github.com/WWBN/AVideo/commit/345711562621d879e63a817d01a229bf0aae7a1d
- https://github.com/WWBN/AVideo
- https://hackerdna.com/courses/cve/cve-2024-34899
