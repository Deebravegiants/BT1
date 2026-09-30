# [M] Header Injection

## Summary
Severity: Medium
Advisory: GHSA-9h73-w7ch-rh73
CVE: CVE-2018-1000883
CWE: CWE-20
Ecosystem: Hex
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-9h73-w7ch-rh73
Type: github-advisory

## Affected
- Hex: `plug` — affected >=0 <1.0.6
- Hex: `plug` — affected >=1.1.0 <1.1.9
- Hex: `plug` — affected >=1.2.0 <1.2.5
- Hex: `plug` — affected >=1.3.0 <1.3.5

## Details
Elixir Plug Plug version All contains a Header Injection vulnerability in Connection that can result in Given a cookie value, Headers can be added. This attack appear to be exploitable via Crafting a value to be sent as a cookie. This vulnerability appears to have been fixed in >= 1.3.5 or ~> 1.2.5 or ~> 1.1.9 or ~> 1.0.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000883
- https://github.com/elixir-plug/plug/commit/8857f8ab4acf9b9c22e80480dae2636692f5f573
- https://github.com/dependabot/elixir-security-advisories/blob/master/packages/plug/2017-04-17.yml
- https://github.com/elixir-plug/plug
