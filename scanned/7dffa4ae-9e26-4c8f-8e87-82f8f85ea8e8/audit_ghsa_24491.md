# [C] CodeIgniter and Kohana vulnerable to PHP Object Injection

## Summary
Severity: Critical
Advisory: GHSA-w9ph-q4h9-rwq6
CVE: CVE-2014-8684
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w9ph-q4h9-rwq6
Type: github-advisory

## Affected
- Packagist: `codeigniter/framework` — affected >=0 <3.0.0
- Packagist: `kohana/core` — affected >=0 <3.3.3

## Details
CodeIgniter before 3.0 and Kohana 3.2.3 and earlier and 3.3.x through 3.3.2 make it easier for remote attackers to spoof session cookies and consequently conduct PHP object injection attacks by leveraging use of standard string comparison operators to compare cryptographic hashes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8684
- https://github.com/kohana/core/pull/492
- https://github.com/kohana/core/commit/66b409a6da2960130888989534ff1799532b8f32
- https://github.com/bcit-ci/CodeIgniter/blob/2.2.6/system/libraries/Session.php#L159
- https://web.archive.org/web/20140802041151/https://scott.arciszewski.me/research/full/php-framework-timing-attacks-object-injection
- http://packetstormsecurity.com/files/130609/Seagate-Business-NAS-Unauthenticated-Remote-Command-Execution.html
- http://seclists.org/fulldisclosure/2014/May/54
