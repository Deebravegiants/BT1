# [M] CVE-2021-43337

## Summary
Severity: Medium
Advisory: CVE-2021-43337
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-11-17
Source: https://osv.dev/vulnerability/CVE-2021-43337
Type: osv

## Details
SchedMD Slurm 21.08.* before 21.08.4 has Incorrect Access Control. On sites using the new AccountingStoreFlags=job_script and/or job_env options, the access control rules in SlurmDBD may permit users to request job scripts and environment files to which they should not have access.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5VY34WSSPRPA6MISNYBZWHSGX2SYSEEE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DUWNGDQTS7AWFI7FIHUWQOYJSD2IQTCG/
- https://lists.schedmd.com/pipermail/slurm-announce/
- https://lists.schedmd.com/pipermail/slurm-announce/2021/000068.html
- https://www.schedmd.com/news.php
- https://www.schedmd.com/news.php?id=256
