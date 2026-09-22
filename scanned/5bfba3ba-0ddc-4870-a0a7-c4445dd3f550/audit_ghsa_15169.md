# [H] Omniauth::MicrosoftGraph Account takeover (nOAuth)

## Summary
Severity: High
Advisory: GHSA-5g66-628f-7cvj
CVE: CVE-2024-21632
CWE: CWE-287
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-5g66-628f-7cvj
Type: github-advisory

## Affected
- RubyGems: `omniauth-microsoft_graph` — affected >=0 <2.0.0

## Details
### Summary
The implementation did not validate the legitimacy of the `email` attribute of the user nor did it give/document an option to do so, making it susceptible to [nOAuth](https://www.descope.com/blog/post/noauth) misconfiguration in cases when the `email` is used as a trusted user identifier

## References
- https://github.com/synth/omniauth-microsoft_graph/security/advisories/GHSA-5g66-628f-7cvj
- https://nvd.nist.gov/vuln/detail/CVE-2024-21632
- https://github.com/synth/omniauth-microsoft_graph/commit/5ffd62690ca0e46978f2fc7d83b18d28edde7795
- https://github.com/synth/omniauth-microsoft_graph/commit/f132078389612b797c872b45bd0e0b47382414c1
- https://github.com/synth/omniauth-microsoft_graph
- https://www.descope.com/blog/post/noauth
