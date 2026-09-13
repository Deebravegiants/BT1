# [H] CVE-2017-9604

## Summary
Severity: High
Advisory: CVE-2017-9604
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-13
Source: https://osv.dev/vulnerability/CVE-2017-9604
Type: osv

## Details
KDE kmail before 5.5.2 and messagelib before 5.5.2, as distributed in KDE Applications before 17.04.2, do not ensure that a plugin's sign/encrypt action occurs during use of the Send Later feature, which allows remote attackers to obtain sensitive information by sniffing the network.

## References
- https://commits.kde.org/kmail/78c5552be2f00a4ac25bd77ca39386522fca70a8
- https://commits.kde.org/messagelib/c54706e990bbd6498e7b1597ec7900bc809e8197
