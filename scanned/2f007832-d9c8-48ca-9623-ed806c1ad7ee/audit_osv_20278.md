# [M] CVE-2021-32689

## Summary
Severity: Medium
Advisory: CVE-2021-32689
Aliases: GHSA-xv6f-344w-895c
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-32689
Type: osv

## Details
Nextcloud Talk is a fully on-premises audio/video and chat communication service. In versions prior to 11.2.2, if a user was able to reuse an earlier used username, they could get access to any chat message sent to the previous user with this username. The issue was patched in versions 11.2.2 and 11.3.0. As a workaround, don't allow users to choose usernames themselves. This is the default behaviour of Nextcloud, but some user providers may allow doing so.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-xv6f-344w-895c
- https://github.com/nextcloud/spreed/releases/tag/v11.2.2
- https://github.com/nextcloud/spreed/releases/tag/v11.3.0
- https://hackerone.com/reports/1200700
- https://github.com/nextcloud/spreed/pull/5633
