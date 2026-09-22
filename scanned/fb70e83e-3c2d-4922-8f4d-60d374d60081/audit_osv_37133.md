# [C] Rocket.Chat: Users can login with any password via the EE ddp-streamer-service

## Summary
Severity: Critical
Advisory: CVE-2026-28514
Aliases: GHSA-w6vw-mrgv-69vf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28514
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to versions 7.8.6, 7.9.8, 7.10.7, 7.11.4, 7.12.4, 7.13.3, and 8.0.0, a critical authentication bypass vulnerability exists in Rocket.Chat's account service used in the ddp-streamer micro service that allows an attacker to log in to the service as any user with a password set, using any arbitrary password. The vulnerability stems from a missing await keyword when calling an asynchronous password validation function, causing a Promise object (which is always truthy) to be evaluated instead of the actual boolean validation result. This may lead to account takeover of any user whose username is known or guessable. This issue has been patched in versions 7.8.6, 7.9.8, 7.10.7, 7.11.4, 7.12.4, 7.13.3, and 8.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28514.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-w6vw-mrgv-69vf
- https://nvd.nist.gov/vuln/detail/CVE-2026-28514
- https://github.com/RocketChat/Rocket.Chat/commit/7d89aae0b1bd08e82b02ceab4c180b430e2c6f07
- https://github.com/RocketChat/Rocket.Chat/pull/37143
