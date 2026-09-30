# [C] Rocket.Chat: Email Parameter Fallback Leads To Account Takeover Within Apple OAuth

## Summary
Severity: Critical
Advisory: CVE-2026-55666
Aliases: GHSA-wx3c-76rf-wpwf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-55666
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.1, 8.4.4, 8.3.6, 8.2.6, 8.1.6, 8.0.7, and 7.10.13, in apps/meteor/app/apple/server/loginHandler.ts, handleIdentityToken parses a JWT issued by Apple during the OAuth flow. The try block checks for an email parameter. If the JWT does not contain an email address, the application falls back to accepting an arbitrary email value supplied directly in the request. Attackers are able to forge Apple JWTs that do not contain an email address and leverage this vulnerability to carry out account takeover attacks. This vulnerability is fixed in 8.5.1, 8.4.4, 8.3.6, 8.2.6, 8.1.6, 8.0.7, and 7.10.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55666.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-wx3c-76rf-wpwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-55666
