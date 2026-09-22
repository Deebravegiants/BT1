# [M] CVE-2021-23827

## Summary
Severity: Medium
Advisory: CVE-2021-23827
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-23827
Type: osv

## Details
Keybase Desktop Client before 5.6.0 on Windows and macOS, and before 5.6.1 on Linux, allows an attacker to obtain potentially sensitive media (such as private pictures) in the Cache and uploadtemps directories. It fails to effectively clear cached pictures, even after deletion via normal methodology within the client, or by utilizing the "Explode message/Explode now" functionality. Local filesystem access is needed by the attacker.

## References
- https://github.com/keybase/client/releases
- https://hackerone.com/reports/1074930
- https://johnjhacking.com/blog/cve-2021-23827/
