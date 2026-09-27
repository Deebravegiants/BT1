# [H] CVE-2021-21399

## Summary
Severity: High
Advisory: CVE-2021-21399
Aliases: GHSA-p9pm-j95j-5mjf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-13
Source: https://osv.dev/vulnerability/CVE-2021-21399
Type: osv

## Details
Ampache is a web based audio/video streaming application and file manager. Versions prior to 4.4.1 allow unauthenticated access to Ampache using the subsonic API. To successfully make the attack you must use a username that is not part of the site to bypass the auth checks. For more details and workaround guidance see the referenced GitHub security advisory.

## References
- https://github.com/ampache/ampache/security/advisories/GHSA-p9pm-j95j-5mjf
