# [M] CVE-2020-11880

## Summary
Severity: Medium
Advisory: CVE-2020-11880
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-04-17
Source: https://osv.dev/vulnerability/CVE-2020-11880
Type: osv

## Details
An issue was discovered in KDE KMail before 19.12.3. By using the proprietary (non-RFC6068) "mailto?attach=..." parameter, a website (or other source of mailto links) can make KMail attach local files to a composed email message without showing a warning to the user, as demonstrated by an attach=.bash_history value.

## References
- https://cgit.kde.org/kmail.git/tag/?h=v19.12.3
- https://cgit.kde.org/kmail.git/commit/?id=2a348eccd352260f192d9b449492071bbf2b34b1
