# [M] CVE-2021-37631

## Summary
Severity: Medium
Advisory: CVE-2021-37631
Aliases: GHSA-4mxp-j277-82hr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-37631
Type: osv

## Details
Deck is an open source kanban style organization tool aimed at personal planning and project organization for teams integrated with Nextcloud. In affected versions the Deck application didn't properly check membership of users in a Circle. This allowed other users in the instance to gain access to boards that have been shared with a Circle, even if the user was not a member of the circle. It is recommended that Nextcloud Deck is upgraded to 1.5.1, 1.4.4 or 1.2.9. If you are unable to update it is advised to disable the Deck plugin.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-4mxp-j277-82hr
- https://hackerone.com/reports/1256021
- https://hackerone.com/reports/1280931
- https://github.com/nextcloud/deck/pull/3217
