# [M] CVE-2017-0936

## Summary
Severity: Medium
Advisory: CVE-2017-0936
CVSS: 5.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-03-28
Source: https://osv.dev/vulnerability/CVE-2017-0936
Type: osv

## Details
Nextcloud Server before 11.0.7 and 12.0.5 suffers from an Authorization Bypass Through User-Controlled Key vulnerability. A missing ownership check allowed logged-in users to change the scope of app passwords of other users. Note that the app passwords themselves where neither disclosed nor could the error be misused to identify as another user.

## References
- https://hackerone.com/reports/297751
- https://nextcloud.com/security/advisory/?id=nc-sa-2018-001
