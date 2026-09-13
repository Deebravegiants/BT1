# [H] CVE-2017-11681

## Summary
Severity: High
Advisory: CVE-2017-11681
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/CVE-2017-11681
Type: osv

## Details
Incorrect Access Control vulnerability in Hashtopussy 0.4.0 allows remote authenticated users to execute actions that should only be available for administrative roles, as demonstrated by an action=createVoucher request to agents.php.

## References
- https://github.com/s3inlc/hashtopussy/issues/241
