# [H] Rocket.Chat: Apple Sign-In skips JWT claims validation, allowing expired and cross-audience token replay

## Summary
Severity: High
Advisory: CVE-2026-55759
Aliases: GHSA-c75c-5hc7-j4vp
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-55759
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.1, 8.4.4, 8.3.6, 8.2.6, 8.1.6, 8.0.7, and 7.10.13, Rocket.Chat's Apple Sign-In handler verifies JWT signatures but skips claims validation. Any Apple-signed JWT with a non-empty iss is accepted regardless of aud, exp, nbf, or nonce. An attacker who obtains a target user's Apple identity token (from server logs, an intercepted sign-in flow, or another application sharing the same Apple developer team) can replay it to authenticate as that user, with no expiration on the replay window. This vulnerability is fixed in 8.5.1, 8.4.4, 8.3.6, 8.2.6, 8.1.6, 8.0.7, and 7.10.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55759.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-c75c-5hc7-j4vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55759
