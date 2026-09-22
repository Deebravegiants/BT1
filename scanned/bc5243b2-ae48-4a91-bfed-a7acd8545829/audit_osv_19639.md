# [H] CVE-2021-23154

## Summary
Severity: High
Advisory: CVE-2021-23154
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-23154
Type: osv

## Details
In Lens prior to 5.3.4, custom helm chart configuration creates helm commands from string concatenation of provided arguments which are then executed in the user's shell. Arguments can be provided which cause arbitrary shell commands to run on the system.

## References
- https://github.com/Mirantis/security/blob/main/advisories/0003.md
