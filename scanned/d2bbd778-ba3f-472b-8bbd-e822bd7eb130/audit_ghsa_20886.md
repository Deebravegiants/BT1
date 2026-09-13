# [C] Pebble Templates protection mechanism bypass can lead to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-wxx5-w9jc-48wx
CVE: CVE-2022-37767
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-13
Source: https://github.com/advisories/GHSA-wxx5-w9jc-48wx
Type: github-advisory

## Affected
- Maven: `io.pebbletemplates:pebble` — affected >=0

## Details
Pebble Templates 3.1.5 allows attackers to bypass a protection mechanism and implement arbitrary code execution with springbok.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37767
- https://github.com/PebbleTemplates/pebble/issues/625#issuecomment-1282138635
- https://github.com/Y4tacker/Web-Security/issues/3
