# [M] Easy!Appointments Denial of Service (DoS)

## Summary
Severity: Medium
Advisory: GHSA-hcjv-982c-5f29
CVE: CVE-2025-29448
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-07
Source: https://github.com/advisories/GHSA-hcjv-982c-5f29
Type: github-advisory

## Affected
- Packagist: `alextselegidis/easyappointments` — affected >=0

## Details
Booking logic flaw in Easy!Appointments v1.5.1 allows unauthenticated attackers to create appointments with excessively long durations, causing a denial of service by blocking all future booking availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-29448
- https://github.com/alextselegidis/easyappointments/commit/74633b60f28bdef3cc9f905c0599cef121fee32b
- https://github.com/Abdullah4eb/CVE-2025-29448
- https://github.com/alextselegidis/easyappointments
