# [H] CVE-2021-31215

## Summary
Severity: High
Advisory: CVE-2021-31215
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-31215
Type: osv

## Details
SchedMD Slurm before 20.02.7 and 20.03.x through 20.11.x before 20.11.7 allows remote code execution as SlurmUser because use of a PrologSlurmctld or EpilogSlurmctld script leads to environment mishandling.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3ODMJQNY4FAV7G3DSKVIO5KY7Q7DKBPU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PRHTASFAU5FNB2MJOG67YID2ONQS5MCQ/
- https://lists.debian.org/debian-lts-announce/2022/01/msg00011.html
- https://lists.schedmd.com/pipermail/slurm-announce/2021/000055.html
- https://www.schedmd.com/news.php?id=248#OPT_248
