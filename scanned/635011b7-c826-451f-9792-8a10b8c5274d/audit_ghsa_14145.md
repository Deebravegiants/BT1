# [C] AzuraCast missing brute force prevention

## Summary
Severity: Critical
Advisory: GHSA-4m7v-wr6v-2mw5
CVE: CVE-2023-2531
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-4m7v-wr6v-2mw5
Type: github-advisory

## Affected
- Packagist: `azuracast/azuracast` — affected >=0 <0.18.3

## Details
The request rate limiting feature on the login page of AzuraCast before version 0.18.3 can be bypassed, which could allow an attacker to brute force login credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2531
- https://github.com/azuracast/azuracast/commit/bdb23594ad3e0c47c8568ce028a7c244a406cf9d
- https://github.com/azuracast/azuracast
- https://huntr.dev/bounties/20463eb2-0f9d-4ea3-a2c8-93f80e7aca02
