# [M] CVE-2018-20345

## Summary
Severity: Medium
Advisory: CVE-2018-20345
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/CVE-2018-20345
Type: osv

## Details
Incorrect access control in StackStorm API (st2api) in StackStorm before 2.9.2 and 2.10.x before 2.10.1 allows an attacker (who has a StackStorm account and is authenticated against the StackStorm API) to retrieve datastore items for other users by utilizing the /v1/keys "?scope=all" and "?user=<username>" query filter parameters. Enterprise editions with RBAC enabled are not affected.

## References
- https://stackstorm.com/2018/12/20/stackstorm-v2-9-2-and-v2-10-1-a-security-release/
