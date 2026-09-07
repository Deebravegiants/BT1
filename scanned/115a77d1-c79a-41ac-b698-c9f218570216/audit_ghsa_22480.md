# [C] Moodle command execution vulnerability exists in the default legacy spellchecker plugin

## Summary
Severity: Critical
Advisory: GHSA-c7jj-vfmr-j9mj
CVE: CVE-2021-21809
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c7jj-vfmr-j9mj
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected 3.10.0
- Packagist: `moodle/moodle` — affected 3.11.2
- Packagist: `moodle/moodle` — affected 3.8.0

## Details
A command execution vulnerability exists in the default legacy spellchecker plugin in a few Moodle multiple specific versions. A specially crafted series of HTTP requests can lead to command execution. An attacker must have administrator privileges to exploit this vulnerabilities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21809
- https://github.com/moodle/moodle
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1277
- http://packetstormsecurity.com/files/164481/Moodle-SpellChecker-Path-Authenticated-Remote-Command-Execution.html
