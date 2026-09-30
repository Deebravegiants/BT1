# [M] TeamPass Improper Privilege Management

## Summary
Severity: Medium
Advisory: GHSA-xvjf-394g-phrr
CVE: CVE-2017-15053
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xvjf-394g-phrr
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <2.1.27.9

## Details
TeamPass before 2.1.27.9 does not properly enforce manager access control when requesting roles.queries.php. It is then possible for a manager user to modify any arbitrary roles within the application, or delete any arbitrary role. To exploit the vulnerability, an authenticated attacker must have the manager rights on the application, then tamper with the requests sent directly, for example by changing the "id" parameter when invoking "delete_role" on roles.queries.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15053
- https://github.com/nilsteampassnet/TeamPass/commit/ef32e9c28b6ddc33cee8a25255bc8da54434af3e
- https://github.com/nilsteampassnet/TeamPass
- http://blog.amossys.fr/teampass-multiple-cve-01.html
