# [H] Cockpit Content Platform vulnerable to 2FA bypass

## Summary
Severity: High
Advisory: GHSA-8wj3-cpmr-8whp
CVE: CVE-2022-2818
CWE: CWE-212, CWE-287, CWE-305
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-16
Source: https://github.com/advisories/GHSA-8wj3-cpmr-8whp
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.2.2

## Details
Cockpit Content Platform through version 2.2.1 is vulnerable to a two-factor authentication (2FA) bypass. The 2FA secret is disclosed in a JWT token after user logs into their account, allowing an attacker to bypass the 2FA code. A patch is available on the `develop` branch and is expected to be part of version 2.2.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2818
- https://github.com/cockpit-hq/cockpit/commit/4bee1b903ee20818f4a8ecb9d974b9536cc54cb4
- https://github.com/cockpit-hq/cockpit
- https://huntr.dev/bounties/ee27e5df-516b-4cf4-9f28-346d907b5491
