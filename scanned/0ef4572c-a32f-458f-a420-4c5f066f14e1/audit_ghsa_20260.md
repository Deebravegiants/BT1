# [H] NocoDB information disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-mx8q-jqwm-85mv
CVE: CVE-2022-2062
CWE: CWE-200, CWE-209, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-14
Source: https://github.com/advisories/GHSA-mx8q-jqwm-85mv
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.91.7

## Details
In NocoDB prior to 0.91.7, the SMTP plugin doesn't have verification or validation. This allows attackers to make requests to internal servers and read the contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2062
- https://github.com/nocodb/nocodb/commit/a18f5dd53811b9ec1c1bb2fdbfb328c0c87d7fb4
- https://github.com/nocodb/nocodb
- https://huntr.dev/bounties/35593b4c-f127-4699-8ad3-f0b2203a8ef6
