# [C] CVE-2019-7587

## Summary
Severity: Critical
Advisory: CVE-2019-7587
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-07
Source: https://osv.dev/vulnerability/CVE-2019-7587
Type: osv

## Details
Bo-blog Wind through 1.6.0-r allows SQL Injection via the admin.php/comments/batchdel/ comID parameter because this parameter is mishandled in the mode/admin.mode.php delBlockedBatch function.

## References
- https://c3tsec.wordpress.com/2019/01/12/sql-injection-in-bo-blog-wind-cms/
