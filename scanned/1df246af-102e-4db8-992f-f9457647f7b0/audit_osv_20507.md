# [C] CVE-2021-34422

## Summary
Severity: Critical
Advisory: CVE-2021-34422
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-11-11
Source: https://osv.dev/vulnerability/CVE-2021-34422
Type: osv

## Details
The Keybase Client for Windows before version 5.7.0 contains a path traversal vulnerability when checking the name of a file uploaded to a team folder. A malicious user could upload a file to a shared folder with a specially crafted file name which could allow a user to execute an application which was not intended on their host machine. If a malicious user leveraged this issue with the public folder sharing feature of the Keybase client, this could lead to remote code execution.

## References
- https://explore.zoom.us/en/trust/security/security-bulletin
