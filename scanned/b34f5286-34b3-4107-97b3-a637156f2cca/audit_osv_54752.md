# [H] CVE-2024-36041

## Summary
Severity: High
Advisory: CVE-2024-36041
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-36041
Type: osv

## Details
KSmserver in KDE Plasma Workspace (aka plasma-workspace) before 5.27.11.1 and 6.x before 6.0.5.1 allows connections via ICE based purely on the host, i.e., all local connections are accepted. This allows another user on the same machine to gain access to the session manager, e.g., use the session-restore feature to execute arbitrary code as the victim (on the next boot) via earlier use of the /tmp directory.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/43YGQJGB5I33UBRY2OHXTPXIEESZLZ6N/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DNOZWSWXAR6EM3VIUJRSAI3L4QPURQPC/
- https://invent.kde.org/plasma/plasma-workspace/
- https://www.x.org/releases/X11R7.7/doc/libSM/xsmp.html
- https://github.com/KDE/plasma-workspace/tags
- https://kde.org/info/security/advisory-20240531-1.txt
