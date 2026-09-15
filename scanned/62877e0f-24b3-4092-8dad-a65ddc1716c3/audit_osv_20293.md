# [C] CVE-2021-32726

## Summary
Severity: Critical
Advisory: CVE-2021-32726
Aliases: GHSA-6qr9-c846-j8mg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-32726
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. In versions prior to 19.0.13, 20.011, and 21.0.3, webauthn tokens were not deleted after a user has been deleted. If a victim reused an earlier used username, the previous user could gain access to their account. The issue was fixed in versions 19.0.13, 20.0.11, and 21.0.3. There are no known workarounds.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-6qr9-c846-j8mg
- https://github.com/nextcloud/server/pull/27532
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1202590
