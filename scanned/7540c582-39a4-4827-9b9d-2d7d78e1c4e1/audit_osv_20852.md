# [M] CVE-2021-37630

## Summary
Severity: Medium
Advisory: CVE-2021-37630
Aliases: GHSA-56j9-3rj4-wvgm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-37630
Type: osv

## Details
Nextcloud Circles is an open source social network built for the nextcloud ecosystem. In affected versions the Nextcloud Circles application allowed any user to join any "Secret Circle" without approval by the Circle owner leaking private information. It is recommended that Nextcloud Circles is upgraded to 0.19.15, 0.20.11 or 0.21.4. There are no workarounds for this issue.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-56j9-3rj4-wvgm
- https://hackerone.com/reports/1257624
- https://github.com/nextcloud/circles/pull/768
