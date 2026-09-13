# [M] CVE-2019-9482

## Summary
Severity: Medium
Advisory: CVE-2019-9482
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-01
Source: https://osv.dev/vulnerability/CVE-2019-9482
Type: osv

## Details
In MISP 2.4.102, an authenticated user can view sightings that they should not be eligible for. Exploiting this requires access to the event that has received the sighting. The issue affects instances with restrictive sighting settings (event only / sighting reported only).

## References
- https://github.com/MISP/MISP/commit/c69969329d197bcdd04832b03310fa73f4eb7155
