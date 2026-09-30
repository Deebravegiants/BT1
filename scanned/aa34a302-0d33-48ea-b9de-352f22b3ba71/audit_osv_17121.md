# [H] CVE-2020-12693

## Summary
Severity: High
Advisory: CVE-2020-12693
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/CVE-2020-12693
Type: osv

## Details
Slurm 19.05.x before 19.05.7 and 20.02.x before 20.02.3, in the rare case where Message Aggregation is enabled, allows Authentication Bypass via an Alternate Path or Channel. A race condition allows a user to launch a process as an arbitrary user.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KNL5E5SK4WP6M3DKU4IKW2NPQD2XTZ4Y/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T3RGQB3EWDLOLTSPAJPPWZEPQK3O3AUH/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00063.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00011.html
- https://lists.schedmd.com/pipermail/slurm-announce/2020/000036.html
- https://www.debian.org/security/2021/dsa-4841
- https://www.schedmd.com/news.php?id=236
