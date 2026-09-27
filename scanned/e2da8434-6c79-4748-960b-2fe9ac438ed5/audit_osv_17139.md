# [H] CVE-2020-12846

## Summary
Severity: High
Advisory: CVE-2020-12846
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2020-12846
Type: osv

## Details
Zimbra before 8.8.15 Patch 10 and 9.x before 9.0.0 Patch 3 allows remote code execution via an avatar file. There is potential abuse of /service/upload servlet in the webmail subsystem. A user can upload executable files (exe,sh,bat,jar) in the Contact section of the mailbox as an avatar image for a contact. A user will receive a "Corrupt File" error, but the file is still uploaded and stored locally in /opt/zimbra/data/tmp/upload/, leaving it open to possible remote execution.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P3
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
