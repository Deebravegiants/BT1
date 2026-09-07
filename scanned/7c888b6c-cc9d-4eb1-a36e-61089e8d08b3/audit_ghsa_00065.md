# [C] active-support impersonates 'activesupport' gem

## Summary
Severity: Critical
Advisory: GHSA-2j55-pcw5-x4h2
CVE: CVE-2018-3779
CWE: CWE-77
Ecosystem: RubyGems
Published: 2018-08-13
Source: https://github.com/advisories/GHSA-2j55-pcw5-x4h2
Type: github-advisory

## Affected
- RubyGems: `active-support` — affected >=0

## Details
The `active-support` ruby gem gem is malware and duplicates the official `activesupport` (no hyphen) gem, but adds a compiled extension. The extension attempts to resolve a base64 encoded domain (29faea63.planfhntage.de), downloads a payload, and executes.
 
This trojan horse gem could allow a remote attacker to execute arbitrary code on the system, caused by containing a malicious backdoor. An attacker could exploit this vulnerability to execute arbitrary code on the system.  No version of this gem should be considered safe.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3779
- https://hackerone.com/reports/392311
- https://github.com/advisories/GHSA-2j55-pcw5-x4h2
