# [H] CVE-2021-47336

## Summary
Severity: High
Advisory: CVE-2021-47336
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47336
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

smackfs: restrict bytes count in smk_set_cipso()

Oops, I failed to update subject line.

From 07571157c91b98ce1a4aa70967531e64b78e8346 Mon Sep 17 00:00:00 2001
Date: Mon, 12 Apr 2021 22:25:06 +0900
Subject: [PATCH] smackfs: restrict bytes count in smk_set_cipso()

Commit 7ef4c19d245f3dc2 ("smackfs: restrict bytes count in smackfs write
functions") missed that count > SMK_CIPSOMAX check applies to only
format == SMK_FIXED24_FMT case.

## References
- https://git.kernel.org/stable/c/5f9880403e6b71d56924748ba331daf836243fca
- https://git.kernel.org/stable/c/8f5c773a2871cf446e3f36b2834fb25bbb28512b
- https://git.kernel.org/stable/c/cbd87ba6a13891acf6180783f8234a8b7a3e3d4d
- https://git.kernel.org/stable/c/135122f174c357b7a3e58f40fa5792156c5e93e6
- https://git.kernel.org/stable/c/258fd821f69378453c071b9dd767b298810fc766
- https://git.kernel.org/stable/c/3780348c1a0e14ffefcaf1fc521f815bcaac94b0
- https://git.kernel.org/stable/c/49ec114a6e62d8d320037ce71c1aaf9650b3cafd
- https://git.kernel.org/stable/c/5c2dca9a7a7ff6a2df34158903515e2e4fd3d2b2
