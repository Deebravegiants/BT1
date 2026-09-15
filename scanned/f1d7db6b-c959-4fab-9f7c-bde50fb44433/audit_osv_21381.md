# [H] CVE-2021-42561

## Summary
Severity: High
Advisory: CVE-2021-42561
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-42561
Type: osv

## Details
An issue was discovered in CALDERA 2.8.1. When activated, the Human plugin passes the unsanitized name parameter to a python "os.system" function. This allows attackers to use shell metacharacters (e.g., backticks "``" or dollar parenthesis "$()" ) in order to escape the current command and execute arbitrary shell commands.

## References
- https://github.com/mitre/caldera/releases
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2021-42561-Command%20Injection%20Via%20the%20Human%20Plugin-MITRE%20Caldera
