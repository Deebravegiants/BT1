# [C] CVE-2026-58066

## Summary
Severity: Critical
Advisory: CVE-2026-58066
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-58066
Type: osv

## Details
Rocket.Chat's SAML SSO before versions 8.7.0, 8.6.1, 8.5.2, 8.4.5, 8.3.7, 8.2.7, 8.1.7, 8.0.8, and 7.10.14 verified XML signatures but did not bind the validated signature to samlp:Response / saml:Assertion. An attacker could submit a wrapped document carrying forged identity attributes alongside any valid signature made by the trusted IdP certificate, and log in as an arbitrary user.

## References
- https://hackerone.com/reports/3827674
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58066.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58066
- https://github.com/RocketChat/Rocket.Chat/pull/41233
