# [H] Parsedown Class-Name Injection

## Summary
Severity: High
Advisory: GHSA-62m3-fc7f-jpp8
CVE: CVE-2019-10905
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-62m3-fc7f-jpp8
Type: github-advisory

## Affected
- Packagist: `erusev/parsedown` — affected >=0 <1.7.2

## Details
Parsedown before 1.7.2, when safe mode is used and HTML markup is disabled, might allow attackers to execute arbitrary JavaScript code if a script (already running on the affected page) executes the contents of any element with a specific class. This occurs because spaces are permitted in code block infostrings, which interferes with the intended behavior of a single class name beginning with the language- substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10905
- https://github.com/erusev/parsedown/issues/699
- https://github.com/FriendsOfPHP/security-advisories/blob/master/erusev/parsedown/CVE-2019-10905.yaml
- https://github.com/erusev/parsedown
- https://github.com/erusev/parsedown/releases/tag/1.7.2
