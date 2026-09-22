# [H] CVE-2021-41177

## Summary
Severity: High
Advisory: CVE-2021-41177
Aliases: GHSA-fj39-4qx4-m3f2
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-41177
Type: osv

## Details
Nextcloud is an open-source, self-hosted productivity platform. Prior to versions 20.0.13, 21.0.5, and 22.2.0, Nextcloud Server did not implement a database backend for rate-limiting purposes. Any component of Nextcloud using rate-limits (as as `AnonRateThrottle` or `UserRateThrottle`) was thus not rate limited on instances not having a memory cache backend configured. In the case of a default installation, this would notably include the rate-limits on the two factor codes. It is recommended that the Nextcloud Server be upgraded to 20.0.13, 21.0.5, or 22.2.0. As a workaround, enable a memory cache backend in `config.php`.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-fj39-4qx4-m3f2
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1265709
- https://github.com/nextcloud/server/pull/28728
