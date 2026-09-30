# [M] CVE-2016-9129

## Summary
Severity: Medium
Advisory: CVE-2016-9129
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-03-28
Source: https://osv.dev/vulnerability/CVE-2016-9129
Type: osv

## Details
Revive Adserver before 3.2.3 suffers from Information Exposure Through Discrepancy. It is possible to check whether or not an email address was associated to one or more user accounts on a target Revive Adserver instance by examining the message printed by the password recovery system. Such information cannot however be used directly to log in to the system, which requires a username.

## References
- https://hackerone.com/reports/98612
- https://github.com/revive-adserver/revive-adserver/commit/38223a841190bebd7a137c7bed84fbbcb2b0c2a5
- https://www.revive-adserver.com/security/revive-sa-2016-001/
