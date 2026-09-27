# [H] Vuetify has a Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-3jp5-5f8r-q2wg
CVE: CVE-2025-8083
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-3jp5-5f8r-q2wg
Type: github-advisory

## Affected
- npm: `vuetify` — affected >=2.2.0-beta.2 <3.0.0-alpha.10

## Details
The Preset configuration feature of Vuetify is vulnerable to Prototype Pollution due to the internal 'mergeDeep' utility function used to merge options with defaults. Using a specially-crafted, malicious preset can result in polluting all JavaScript objects with arbitrary properties, which can further negatively affect all aspects of the application's behavior. This can lead to a wide range of security issues, including resource exhaustion/denial of service or unauthorized access to data.

If the application utilizes Server-Side Rendering (SSR), this vulnerability could affect the whole server process.

This issue affects Vuetify versions greater than or equal to 2.2.0-beta.2 and less than 3.0.0-alpha.10.

Note:
Version 2.x of Vuetify is End-of-Life and will not receive any updates to address this issue. For more information see  here https://v2.vuetifyjs.com/en/about/eol/ .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8083
- https://codepen.io/herodevs/pen/RNWoaQM/f1f4ccc7e6a307c2a8c36d948ba14755
- https://github.com/vuetifyjs/vuetify
- https://www.herodevs.com/vulnerability-directory/cve-2025-8083
