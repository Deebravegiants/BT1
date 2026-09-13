# [M] Unauthenticated Denial of Service via Unbounded Activity-Timeline Range in CTI-Transmute

## Summary
Severity: Medium
Advisory: CVE-2026-69079
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69079
Type: osv

## Details
CTI-Transmute contains an uncontrolled resource-consumption vulnerability in the unauthenticated /activity_timeline endpoint. The endpoint accepts a user-controlled days query parameter that was not restricted to a reasonable range.

A remote, unauthenticated attacker could submit an excessively large value for this parameter, causing the application to retrieve and process activity data over an arbitrarily large period. This could consume excessive database, CPU, or memory resources, delay the processing of concurrent requests, or trigger an internal server error. Repeated requests could further degrade the availability of the CTI-Transmute website.

The vulnerability is corrected by clamping the requested timeline range to a minimum of one day and a maximum of 1,095 days.

## References
- https://github.com/MISP/cti-transmute/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69079.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69079
- https://github.com/MISP/cti-transmute/commit/321892d26b82c8a5af1e210ee30735abb109fac2
