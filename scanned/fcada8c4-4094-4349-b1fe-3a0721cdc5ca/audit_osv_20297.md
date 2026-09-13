# [M] CVE-2021-32734

## Summary
Severity: Medium
Advisory: CVE-2021-32734
Aliases: GHSA-6hf5-c2c4-2526
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-32734
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. In versions prior to 19.0.13, 20.011, and 21.0.3, the Nextcloud Text application shipped with Nextcloud Server returned verbatim exception messages to the user. This could result in a full path disclosure on shared files. The issue was fixed in versions 19.0.13, 20.0.11, and 21.0.3. As a workaround, one may disable the Nextcloud Text application in Nextcloud Server app settings.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-6hf5-c2c4-2526
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1246721
- https://github.com/nextcloud/text/pull/1695
