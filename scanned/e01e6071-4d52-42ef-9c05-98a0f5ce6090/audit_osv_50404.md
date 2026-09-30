# [M] CVE-2020-15436

## Summary
Severity: Medium
Advisory: CVE-2020-15436
Aliases: A-174737742, ASB-A-174737742
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2020-15436
Type: osv

## Details
Use-after-free vulnerability in fs/block_dev.c in the Linux kernel before 5.8 allows local users to gain privileges or cause a denial of service by leveraging improper access to a certain error field.

## References
- https://security.netapp.com/advisory/ntap-20201218-0002/
- https://lkml.org/lkml/2020/6/7/379
