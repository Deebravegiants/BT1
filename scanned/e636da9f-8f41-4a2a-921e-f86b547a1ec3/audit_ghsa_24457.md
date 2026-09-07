# [H] MunkiReport Software Update module is vulnerable to SQL injection

## Summary
Severity: High
Advisory: GHSA-4qgh-m9vp-48xp
CVE: CVE-2020-15887
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4qgh-m9vp-48xp
Type: github-advisory

## Affected
- Packagist: `munkireport/softwareupdate` — affected >=0 <1.6

## Details
A SQL injection vulnerability in softwareupdate_controller.php in the Software Update module before 1.6 for MunkiReport allows attackers to execute arbitrary SQL commands via the last URL parameter of the `/module/softwareupdate/get_tab_data/` endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15887
- https://github.com/munkireport/munkireport-php/releases
- https://github.com/munkireport/munkireport-php/releases/tag/v5.6.3
- https://github.com/munkireport/munkireport-php/wiki/20200722-SQL-Injection-in-softwareupdate-module
- https://github.com/munkireport/softwareupdate
- https://github.com/munkireport/softwareupdate/releases
