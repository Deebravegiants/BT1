# [H] Privilege escalation in easyappointments

## Summary
Severity: High
Advisory: GHSA-7f62-4887-cfv5
CVE: CVE-2022-1397
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-11
Source: https://github.com/advisories/GHSA-7f62-4887-cfv5
Type: github-advisory

## Affected
- Packagist: `alextselegidis/easyappointments` — affected >=0

## Details
The Easy!Appointments API authorization is checked against the user's existence, without validating the permissions. As a result, a low privileged user (eg. provider) can create a new admin user via the "/api/v1/admins/" endpoint and take over the system. A [patch](https://github.com/alextselegidis/easyappointments/commit/63dbb51decfcc1631c398ecd6d30e3a337845526) is available on the `develop` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1397
- https://github.com/alextselegidis/easyappointments/commit/63dbb51decfcc1631c398ecd6d30e3a337845526
- https://github.com/alextselegidis/easyappointments
- https://huntr.dev/bounties/5f69e094-ab8c-47a3-b01d-8c12a3b14c61
