# [C] CVE-2019-11362

## Summary
Severity: Critical
Advisory: CVE-2019-11362
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-20
Source: https://osv.dev/vulnerability/CVE-2019-11362
Type: osv

## Details
app/controllers/frontend/PostController.php in ROCBOSS V2.2.1 has SQL injection via the Post:doReward score paramter, as demonstrated by the /do/reward/3 URI.

## References
- https://github.com/rocboss/ROCBOSS/issues/12
