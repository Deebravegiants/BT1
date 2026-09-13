# [M] CVE-2021-32678

## Summary
Severity: Medium
Advisory: CVE-2021-32678
Aliases: GHSA-48rx-3gmf-g74j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-32678
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. In versions prior to 19.0.13, 20.0.11, and 21.0.3, ratelimits are not applied to OCS API responses. This affects any OCS API controller (`OCSController`) using the `@BruteForceProtection` annotation. Risk depends on the installed applications on the Nextcloud Server, but could range from bypassing authentication ratelimits or spamming other Nextcloud users. The vulnerability is patched in versions 19.0.13, 20.0.11, and 21.0.3. No workarounds aside from upgrading are known to exist.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BVZS26RDME2DYTKET5AECRIZDFUGR2AZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J63NBVPR2AQCAWRNDOZSGRY5II4WS2CZ/
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-48rx-3gmf-g74j
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1214158
- https://github.com/nextcloud/server/pull/27329
