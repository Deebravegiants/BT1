# [M] CVE-2021-46837

## Summary
Severity: Medium
Advisory: CVE-2021-46837
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-30
Source: https://osv.dev/vulnerability/CVE-2021-46837
Type: osv

## Details
res_pjsip_t38 in Sangoma Asterisk 16.x before 16.16.2, 17.x before 17.9.3, and 18.x before 18.2.2, and Certified Asterisk before 16.8-cert7, allows an attacker to trigger a crash by sending an m=image line and zero port in a response to a T.38 re-invite initiated by Asterisk. This is a re-occurrence of the CVE-2019-15297 symptoms but not for exactly the same reason. The crash occurs because there is an append operation relative to the active topology, but this should instead be a replace operation.

## References
- https://downloads.asterisk.org/pub/security/AST-2021-006.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://www.debian.org/security/2022/dsa-5285
