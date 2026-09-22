# [M] CVE-2017-0887

## Summary
Severity: Medium
Advisory: CVE-2017-0887
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-0887
Type: osv

## Details
Nextcloud Server before 9.0.55 and 10.0.2 suffers from a bypass in the quota limitation. Due to not properly sanitizing values provided by the `OC-Total-Length` HTTP header an authenticated adversary may be able to exceed their configured user quota. Thus using more space than allowed by the administrator.

## References
- https://hackerone.com/reports/173622
- https://nextcloud.com/security/advisory/?id=nc-sa-2017-005
