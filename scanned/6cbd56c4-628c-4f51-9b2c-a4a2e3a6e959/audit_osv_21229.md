# [M] CVE-2021-41239

## Summary
Severity: Medium
Advisory: CVE-2021-41239
Aliases: GHSA-g722-cm3h-8wrx
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-03-08
Source: https://osv.dev/vulnerability/CVE-2021-41239
Type: osv

## Details
Nextcloud server is a self hosted system designed to provide cloud style services. In affected versions the User Status API did not consider the user enumeration settings by the administrator. This allowed a user to enumerate other users on the instance, even when user listings where disabled. It is recommended that the Nextcloud Server is upgraded to 20.0.14, 21.0.6 or 22.2.1. There are no known workarounds.

## References
- https://security.gentoo.org/glsa/202208-17
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-g722-cm3h-8wrx
- https://github.com/nextcloud/server/issues/27122
- https://github.com/nextcloud/server/pull/29260
