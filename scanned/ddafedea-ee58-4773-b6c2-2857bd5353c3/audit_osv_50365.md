# [M] CVE-2020-14002

## Summary
Severity: Medium
Advisory: CVE-2020-14002
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-29
Source: https://osv.dev/vulnerability/CVE-2020-14002
Type: osv

## Details
PuTTY 0.68 through 0.73 has an Observable Discrepancy leading to an information leak in the algorithm negotiation. This allows man-in-the-middle attackers to target initial connection attempts (where no host key for the server has been cached by the client).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/26TACCSQYYCPWAJYNAUIXJGZ5RGORJZV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JPV4A77EDCT4BTFO5BE26ZH72BG4E5IJ/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00016.html
- https://lists.tartarus.org/pipermail/putty-announce/
- https://security.netapp.com/advisory/ntap-20200717-0003/
- https://www.chiark.greenend.org.uk/~sgtatham/putty/changes.html
- https://www.fzi.de/en/news/news/detail-en/artikel/fsa-2020-2-ausnutzung-eines-informationslecks-fuer-gezielte-mitm-angriffe-auf-ssh-clients/
