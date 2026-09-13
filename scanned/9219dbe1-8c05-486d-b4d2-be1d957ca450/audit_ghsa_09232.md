# [M] AstrBot Makes Use of Hard-coded Password

## Summary
Severity: Medium
Advisory: GHSA-mq9q-25hm-g4gp
CVE: CVE-2026-7579
CWE: CWE-259
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-01
Source: https://github.com/advisories/GHSA-mq9q-25hm-g4gp
Type: github-advisory

## Affected
- PyPI: `AstrBot` — affected >=0

## Details
A security vulnerability has been detected in AstrBotDevs AstrBot up to 4.16.0. This issue affects some unknown processing of the file astrbot/dashboard/routes/auth.py of the component Dashboard. The manipulation leads to hard-coded credentials. It is possible to initiate the attack remotely. The exploit has been disclosed publicly and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/AstrBotDevs/AstrBot/security/advisories/GHSA-vrqm-xcfv-286r
- https://nvd.nist.gov/vuln/detail/CVE-2026-7579
- https://github.com/AstrBotDevs/AstrBot
- https://github.com/Dave-gilmore-aus/security-advisories/blob/main/AstrBot-Security-Advisory
- https://vuldb.com/submit/793437
- https://vuldb.com/vuln/360420
- https://vuldb.com/vuln/360420/cti
