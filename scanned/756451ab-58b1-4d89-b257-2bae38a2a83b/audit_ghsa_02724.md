# [H] Incorrect Authorization in TeamPass

## Summary
Severity: High
Advisory: GHSA-fv48-hjhp-94c7
CVE: CVE-2020-12477
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-fv48-hjhp-94c7
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0

## Details
The REST API functions in TeamPass 2.1.27.36 allow any user with a valid API token to bypass IP address whitelist restrictions via an X-Forwarded-For client HTTP header to the getIp function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12477
- https://github.com/nilsteampassnet/TeamPass/issues/2761
