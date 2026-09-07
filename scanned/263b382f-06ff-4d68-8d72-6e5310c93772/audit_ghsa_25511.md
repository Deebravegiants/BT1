# [M] Missing authorization in Moodle

## Summary
Severity: Medium
Advisory: GHSA-c5hf-mc85-2hx4
CVE: CVE-2022-0984
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-c5hf-mc85-2hx4
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.6
- Packagist: `moodle/moodle` — affected >=3.10.0 <3.10.10
- Packagist: `moodle/moodle` — affected >=0 <3.9.13

## Details
Users with the capability to configure badge criteria (teachers and managers by default) were able to configure course badges with profile field criteria, which should only be available for site badges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0984
- https://github.com/moodle/moodle/commit/cdc78a16a5da95a17fb10bf1c66689237f5a3f7d
- https://bugzilla.redhat.com/show_bug.cgi?id=2064118
- https://bugzilla.redhat.com/show_bug.cgi?id=2064125
- https://github.com/moodle/moodle
