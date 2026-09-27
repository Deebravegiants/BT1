# [M] CVE-2017-16961

## Summary
Severity: Medium
Advisory: CVE-2017-16961
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-16961
Type: osv

## Details
A SQL injection vulnerability in core/inc/auto-modules.php in BigTree CMS through 4.2.19 allows remote authenticated attackers to obtain information in the context of the user used by the application to retrieve data from the database. The attack uses an admin/trees/add/process request with a crafted _tags[] parameter that is mishandled in a later admin/ajax/dashboard/approve-change request.

## References
- https://github.com/bigtreecms/BigTree-CMS/issues/323
