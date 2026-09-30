# [H] CVE-2021-32705

## Summary
Severity: High
Advisory: CVE-2021-32705
Aliases: GHSA-fjv7-283f-5m54
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-32705
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. In versions prior to 19.0.13, 20.011, and 21.0.3, there was a lack of ratelimiting on the public DAV endpoint. This may have allowed an attacker to enumerate potentially valid share tokens or credentials. The issue was fixed in versions 19.0.13, 20.0.11, and 21.0.3. There are no known workarounds.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BVZS26RDME2DYTKET5AECRIZDFUGR2AZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J63NBVPR2AQCAWRNDOZSGRY5II4WS2CZ/
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-fjv7-283f-5m54
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1192159
- https://github.com/nextcloud/server/pull/27610
