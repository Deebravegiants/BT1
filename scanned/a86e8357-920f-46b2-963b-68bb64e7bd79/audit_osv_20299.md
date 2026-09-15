# [M] CVE-2021-32741

## Summary
Severity: Medium
Advisory: CVE-2021-32741
Aliases: GHSA-crvj-vmf7-xrvr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-32741
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. In versions prior to 19.0.13, 20.011, and 21.0.3, there was a lack of ratelimiting on the public share link mount endpoint. This may have allowed an attacker to enumerate potentially valid share tokens. The issue was fixed in versions 19.0.13, 20.0.11, and 21.0.3. There are no known workarounds.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-crvj-vmf7-xrvr
- https://hackerone.com/reports/1192144
- https://github.com/nextcloud/server/pull/26958
