# [H] Rocket.Chat: 2FA bypass and login of deactivated users via EE ddp-streamer

## Summary
Severity: High
Advisory: CVE-2026-30831
Aliases: GHSA-7qr6-q62g-hm63
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-30831
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to versions 7.10.8, 7.11.5, 7.12.5, 7.13.4, 8.0.2, 8.1.1, and 8.2.0, authentication vulnerabilities exist in Rocket.Chat's enterprise DDP Streamer service. The Account.login method exposed through the DDP Streamer does not enforce Two-Factor Authentication (2FA) or validate user account status (deactivated users can still login), despite these checks being mandatory in the standard Meteor login flow. This issue has been patched in versions 7.10.8, 7.11.5, 7.12.5, 7.13.4, 8.0.2, 8.1.1, and 8.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30831.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-7qr6-q62g-hm63
- https://nvd.nist.gov/vuln/detail/CVE-2026-30831
