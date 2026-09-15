# [C] CVE-2018-19367

## Summary
Severity: Critical
Advisory: CVE-2018-19367
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-20
Source: https://osv.dev/vulnerability/CVE-2018-19367
Type: osv

## Details
Portainer through 1.19.2 provides an API endpoint (/api/users/admin/check) to verify that the admin user is already created. This API endpoint will return 404 if admin was not created and 204 if it was already created. Attackers can set an admin password in the 404 case.

## References
- https://github.com/portainer/portainer/issues/2475
- https://github.com/lichti/shodan-portainer/
