# [H] CVE-2022-24986

## Summary
Severity: High
Advisory: CVE-2022-24986
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-26
Source: https://osv.dev/vulnerability/CVE-2022-24986
Type: osv

## Details
KDE KCron through 21.12.2 uses a temporary file in /tmp when saving, but reuses the filename during an editing session. Thus, someone watching it be created the first time could potentially intercept the file the following time, enabling that person to run unauthorized commands.

## References
- https://apps.kde.org/kcron/
- http://www.openwall.com/lists/oss-security/2022/02/25/3
