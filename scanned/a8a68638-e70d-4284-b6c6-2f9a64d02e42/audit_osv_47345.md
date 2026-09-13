# [M] CVE-2016-2860

## Summary
Severity: Medium
Advisory: CVE-2016-2860
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2016-2860
Type: osv

## Details
The newEntry function in ptserver/ptprocs.c in OpenAFS before 1.6.17 allows remote authenticated users from foreign Kerberos realms to bypass intended access restrictions and create arbitrary groups as administrators by leveraging mishandling of the creator ID.

## References
- http://git.openafs.org/?p=openafs.git%3Ba=commitdiff%3Bh=396240cf070a806b91fea81131d034e1399af1e0
- https://lists.openafs.org/pipermail/openafs-announce/2016/000496.html
- https://www.openafs.org/dl/openafs/1.6.17/RELNOTES-1.6.17
- http://www.debian.org/security/2016/dsa-3569
- http://www.openafs.org/pages/security/OPENAFS-SA-2016-001.txt
