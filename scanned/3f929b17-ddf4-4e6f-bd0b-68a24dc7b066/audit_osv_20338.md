# [M] CVE-2021-32832

## Summary
Severity: Medium
Advisory: CVE-2021-32832
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-30
Source: https://osv.dev/vulnerability/CVE-2021-32832
Type: osv

## Details
Rocket.Chat is an open-source fully customizable communications platform developed in JavaScript. In Rocket.Chat before versions 3.11.3, 3.12.2, and 3.13 an issue with certain regular expressions could lead potentially to Denial of Service. This was fixed in versions 3.11.3, 3.12.2, and 3.13.

## References
- https://docs.rocket.chat/guides/security/security-updates
- https://github.com/RocketChat/Rocket.Chat/releases/tag/3.11.3
- https://github.com/RocketChat/Rocket.Chat/commit/4a0dce973e37ec3f56ca2231d6030511dbdd094c
- https://securitylab.github.com/advisories/GHSL-2020-310-redos-Rocket.Chat/
