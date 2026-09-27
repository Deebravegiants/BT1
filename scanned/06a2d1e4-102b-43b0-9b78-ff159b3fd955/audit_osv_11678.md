# [M] CVE-2017-9268

## Summary
Severity: Medium
Advisory: CVE-2017-9268
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-9268
Type: osv

## Details
In the open build service before 201707022 the wipetrigger and rebuild actions checked the wrong project for permissions, allowing authenticated users to cause operations on projects where they did not have permissions leading to denial of service (resource consumption).

## References
- https://bugzilla.suse.com/show_bug.cgi?id=1045519
- https://github.com/openSUSE/open-build-service/pull/3267
