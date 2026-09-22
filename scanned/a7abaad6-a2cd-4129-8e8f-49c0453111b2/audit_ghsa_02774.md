# [H] Improper Input Validation in Centreon Web

## Summary
Severity: High
Advisory: GHSA-4f26-v6fr-9hmp
CVE: CVE-2019-16405
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-07-28
Source: https://github.com/advisories/GHSA-4f26-v6fr-9hmp
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <18.10.8
- Packagist: `centreon/centreon` — affected >=19.0.0 <19.04.5

## Details
Centreon Web 19.04.4 allows Remote Code Execution by an administrator who can modify Macro Expression location settings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16405
- https://github.com/centreon/centreon/pull/7864
- https://github.com/centreon/centreon/pull/7884
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-18.10.html
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-19.04.html
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-19.10.html
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-2.8.html
- https://github.com/TheCyberGeek/CVE-2019-16405.rb
- https://github.com/centreon/centreon
- https://github.com/centreon/centreon/releases/tag/19.04.5
- https://thecybergeek.co.uk/cves/2019/09/17/CVE-2019-16405-06.html
- https://thecybergeek.co.uk/cves/2019/09/19/CVEs.html
- http://packetstormsecurity.com/files/155999/Centreon-19.04-Remote-Code-Execution.html
